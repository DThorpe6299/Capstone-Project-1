from flask import Flask, redirect, render_template, request, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from models import User, Comment, Meal, MealPlan, db, connect_db
from forms import LoginForm, RegisterForm, CommentForm, MealPlanForm, EditUserForm
from secret import API_Key
from flask_migrate import Migrate
import requests
apiKey=API_Key
API_BASE_URL="https://api.spoonacular.com/mealplanner/generate"

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///meal_plan_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
migrate = Migrate(app, db)

with app.app_context():
    connect_db(app)
    db.create_all()

app.config['SECRET_KEY'] = "Diet_Time"
debug=DebugToolbarExtension(app)
bcrypt=Bcrypt()

@app.route('/')
def index():
    return redirect('/register')

@app.route('/login', methods=["GET", "POST"])
def login():
    """Produce login form or handle login"""
    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        pwd=form.password.data

        user = User.authenticate(username, pwd)
        print(f"User object after authenticate: {user}")
        if user:
            session['user_id']=user.id
            app.logger.info(f"User ID in session after login: {session.get('user_id')}")
            return redirect('/meal_plans')
        else:
            form.username.errors=["Incorrect username/password"]
    return render_template("login.html", form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    """Produce user registration form"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        print(f"Form data - Username: {username}, Password: {password}, Email: {email}")

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template('register.html', form=form, error="Username already exists.")
        elif existing_email:
            return render_template('register.html', form=form, error="Email already exists.")
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            print(f"User ID in session after registration: {session.get('user_id')}")
            return redirect('/meal_plans')
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    """Log the user out."""
    session.pop('user_id')
    return redirect('/login')

@app.route('/users')
def users():
    users=User.query.limit(25).all()
    return render_template('users.html', users=users)

@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user(user_id):
    user=User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if 'user_id' in session:
        if form.validate_on_submit():
            username=form.username.data
            email=form.email.data
            edited_user=User(username=username, email=email)
            db.session.add(edited_user)
            db.session.commit()
            return redirect(f"/users/{user.id}")
    return render_template('edit_user.html', form=form)

@app.route('/users/<int:user_id>')
def user(user_id):
    """Show an instance of a user."""
    if "user_id" in session:
        user=User.query.get_or_404(user_id)
        return render_template('user.html', user=user)
    flash("Please login to continue.", 'danger')
    return redirect('/login')



#Meal Plan Functionality#########################################
@app.route('/meal_plans', methods=['GET','POST'])
def meal_plans():
    if request.method == 'POST':
        app.logger.info(f"Received {request.method} request for meal plans")
    else:
        app.logger.info(f"Received {request.method} request for meal plans")
    
    user_id=session['user_id']
    current_user=User.query.get_or_404(user_id)
    username=current_user.username
    meal_plans = MealPlan.query.filter_by(user_id=user_id).limit(25).all()
    return render_template('meal_plans.html', meal_plans=meal_plans, username=username)

@app.route('/meal_plans/<int:meal_plan_id>', methods=["GET"])
def get_meal_plans(meal_plan_id):
    """Show a meal plan."""
    meal_plan= MealPlan.query.get_or_404(meal_plan_id)
    user_id=session['user_id']
    current_user=User.query.get_or_404(user_id)
    username=current_user.username

    nutrients = {
        'calories': meal_plan.calories,
        'protein': meal_plan.protein,
        'fat': meal_plan.fat,
        'carbohydrates': meal_plan.carbohydrates
    }

    return render_template('meal_plan.html', meal_plan=meal_plan, username=username, nutrients=nutrients)

@app.route('/meal_plans/new', methods=['GET', 'POST'])
def generate_meal_plan():
    print('meal plan form')
    if 'user_id' not in session:
        print('user not in session')
        flash("Please login to continue.", 'danger')
        return redirect("/login")
    form=MealPlanForm()
    print(form.validate_on_submit())
    print('form for meal plan')
    if form.validate_on_submit():
            print('meal plan validation in progress')
            diet = request.form['diet']  
            timeframe = request.form['timeframe']  
            target_calories = request.form['target_calories']  
            exclude = request.form['exclude']
            print('form params')

            print(f"Diet: {diet}")  
            print(f"Timeframe: {timeframe}")  
            print(f"Target Calories: {target_calories}")  
            print(f"Exclude: {exclude}")  


            params = {
                'apiKey': API_Key,
                'diet': diet,
                'timeFrame': timeframe,
                'targetCalories': target_calories,
                'exclude': exclude
            }
            user_id = session['user_id']
            
            response = requests.get(API_BASE_URL, params=params)
            print(response.status_code)
            if response.status_code == 200:
                data = response.json()
                print(data)  
                print('is true')

                
                print(timeframe)
                if timeframe == 'day':
                    print("Day meal plan:")
                    print("Meals:")
                    meals = data["meals"]
                    nutrients = data["nutrients"]
                    for meal in meals:
                        print(f"{meal['title']}: {meal['sourceUrl']}")
                    print("Nutrients:")
                    print(f"Calories: {nutrients['calories']}")
                    print(f"Protein: {nutrients['protein']}")
                    print(f"Fat: {nutrients['fat']}")
                    print(f"Carbohydrates: {nutrients['carbohydrates']}")
                    
                    for meal in meals:
                        new_meal = Meal(
                            in_wishlist=False,
                            user_made_dish=False
                        )
                        db.session.add(new_meal)
                        db.session.flush()  
                        meal_id = new_meal.id

                        
                        meal_plan = MealPlan(
                            user_id=user_id,
                            meal_id=meal_id,
                            diet=diet,
                            timeframe=timeframe,
                            target_calories=target_calories,
                            exclude=exclude,
                            calories=nutrients.get('calories', 0),
                            protein=nutrients.get('protein', 0),
                            fat=nutrients.get('fat', 0),
                            carbohydrates=nutrients.get('carbohydrates', 0)
                            )
                        db.session.add(meal_plan)

                    db.session.commit()
                    return render_template('day_generated_meal_plan.html', meals=meals, nutrients=nutrients)
                else:
                    print("Week meal plan:")
                    week_data = response.json()
                    meals={}

                    for day, data in week_data['week'].items():
                        day_of_week = day.capitalize()
                        meals[day_of_week] = {
                            'meals': data.get('meals', []),
                            'nutrients': data.get('nutrients', {})
                            }
                        nutrients = data.get('nutrients', {})
                        
                        # Use the accessed data as needed for each day
                        print(f"Day: {day_of_week}")
                        print("Meals:")
                        for meal in meals:
                        
                            print("Nutrients:")
                            print(f"Calories: {nutrients.get('calories', 0)}")
                            print(f"Protein: {nutrients.get('protein', 0)}")
                            print(f"Fat: {nutrients.get('fat', 0)}")
                            print(f"Carbohydrates: {nutrients.get('carbohydrates', 0)}")
                        for meal in meals:
                            new_meal = Meal(
                                in_wishlist=False,
                                user_made_dish=False
                            )
                            db.session.add(new_meal)
                            db.session.flush()
                            meal_id = new_meal.id

                            meal_plan = MealPlan(
                            user_id=user_id,
                            meal_id=meal_id,
                            diet=diet,
                            timeframe=timeframe,
                            target_calories=target_calories,
                            exclude=exclude,
                            calories=nutrients.get('calories', 0),
                            protein=nutrients.get('protein', 0),
                            fat=nutrients.get('fat', 0),
                            carbohydrates=nutrients.get('carbohydrates', 0)
                            )
                            db.session.add(meal_plan)

                    db.session.commit()
                    return render_template('week_generated_meal_plan.html', meals=meals)

    return render_template("meal_plan_form.html", form=form)

@app.route('/meal_plans/<int:meal_plan_id>/delete', methods=['POST'])
def delete_meal_plan(meal_plan_id):
    """Delete a meal plan."""
    if 'user_id' not in session:
        flash("Please login to continue.", 'danger')
        return redirect("/login")
    
    meal_plan = MealPlan.query.get_or_404(meal_plan_id)


    db.session.delete(meal_plan)

    db.session.commit()

    return redirect('/meal_plans')

#Comment handling and form#########################################
@app.route('/meals/<int:meal_id>/comments/new', methods=['GET', 'POST'])
def comment_form(meal_id):
    if 'user_id' not in session:
        flash("Please login to continue.", 'danger')
        return redirect("/login")

    user_id = session['user_id']

    # Query the Meal model to check if the user has made this dish
    meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()

    if meal:  # Check if the meal exists and the user has made it
        form = CommentForm()
        if form.validate_on_submit():
            content = form.content.data
            new_comment = Comment(content=content, user_id=user_id, meal_id=meal_id, meal=meal)
            db.session.add(new_comment)
            db.session.commit()
            return redirect('/comments')

        return render_template('comment_form.html', form=form)

    flash("You can only comment on dishes you've made.", 'warning')
    return redirect('/meal_plans')


@app.route('/comments')
def show_comments():
    """Show comments."""
    if 'user_id' not in session:
        flash("Please login to continue.", 'danger')
        return redirect("/login")
    comments=Comment.query.limit(25).all()
    return render_template('comments.html', comments=comments)

@app.route('/comments/<int:comment_id>')
def see_comment(comment_id):
    """Show a comment"""
    if 'user_id' not in session:
        flash("Please login to continue.", 'danger')
        return redirect("/login")
    comment = Comment.query.get_or_404(comment_id)
    return render_template('show_comment.html', comment=comment)

@app.route('/comments/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    comment=Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect('/comments')

app.run(debug=True)