from flask import Flask, redirect, render_template, request, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from models import User, Comment, MealPlan, db, connect_db
from forms import LoginForm, RegisterForm, CommentForm, MealPlanForm, EditUserForm
from secret import API_Key
import requests
apiKey=API_Key
API_BASE_URL="https://api.spoonacular.com/mealplanner/generate"

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///meal_plan_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

with app.app_context():
    connect_db(app)
    db.create_all

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
        if user:
            session['user_id']=user.id
            return redirect('/meal_plan')
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

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template('register.html', form=form, error="Username already exists.")
        elif existing_email:
            return render_template('register.html', form=form, error="Email already exists.")
        else:
            new_user = User(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/login')
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

@app.route('/users/<int:user.id>')
def user(user_id):
    """Show an instance of a user."""
    user=User.query.get_or_404(user_id)
    return render_template('user.html', user=user)



#Meal Plan Functionality#########################################
@app.route('/meal_plans')
def meal_plans():
    meal_plans=MealPlan.query.limit(25).all()
    return render_template('meal_plans.html', meal_plans=meal_plans)

@app.route('/meal_plans/<int:meal_plan_id>', methods=["GET"])
def get_meal_plans(meal_plan_id):
    """Show a meal plan."""
    meal_plan= MealPlan.query.get_or_404(meal_plan_id)
    return render_template('meal_plan.html', meal_plan=meal_plan)

@app.route('/meal_plan/new', methods=['GET', 'POST'])
def generate_meal_plan():
    if 'user_id' not in session:
        flash("Please login to continue.", 'danger')
        return redirect("/login")
    form=MealPlanForm()
    if form.validate_on_submit():
            diet = request.form['diet']  
            timeframe = request.form['timeframe']  
            target_calories = request.form['target_calories']  
            exclude = request.form['exclude']

            params = {
                'apiKey': API_Key,
                'diet': diet,
                'timeframe': timeframe,
                'targetCalories': target_calories,
                'exclude': exclude
            }

            response = requests.get(API_BASE_URL, params=params)

            if response.status_code == 200:
                data = response.json()  
                if "meals" in data and "nutrients" in data:
                    meals = data["meals"]
                    nutrients = data["nutrients"]

                    if params['timeframe'] == 'day':
                        print("Day meal plan:")
                        print("Meals:")
                        for meal in meals:
                            print(f"{meal['title']}: {meal['sourceUrl']}")
                        print("Nutrients:")
                        print(f"Calories: {nutrients['calories']}")
                        print(f"Protein: {nutrients['protein']}")
                        print(f"Fat: {nutrients['fat']}")
                        print(f"Carbohydrates: {nutrients['carbohydrates']}")
                        return render_template('generated_meal_plan.html', meals=meals, nutrients=nutrients)
                    else:
                        print("Week meal plan:")
                        for day, details in data['week'].items():
                            print(f"{day.capitalize()} meal plan:")
                        print("Nutrients:")
                        print(f"Calories: {details['nutrients']['calories']}")
                        print(f"Protein: {details['nutrients']['protein']}")
                        print(f"Fat: {details['nutrients']['fat']}")
                        print(f"Carbohydrates: {details['nutrients']['carbohydrates']}")
                        return render_template('generated_meal_plan.html', meals=meals, nutrients=nutrients)
    return render_template("meal_plan_form.html", form=form)

@app.route('/meal_plan/<int:meal_plan_id>/delete', methods=['POST'])
def delete_meal_plan(meal_plan_id):
    """Delete a meal plan."""
    if 'user_id' not in session:
        flash("Please login to continue.", 'danger')
        return redirect("/login")
    meal_plan=MealPlan.query.get_or_404(meal_plan_id)
    db.session.delete(meal_plan)
    db.session.commit()
    return redirect('/meal_plans')

#Comment handling and form#########################################
@app.route('/comments/new', methods=['GET', 'POST'])
def comment_form():
    """Shows form for a user to add a comment about a dish if they have made it; handles comment submission."""

    if 'user_id' not in session:
        flash("Please login to continue.", 'danger')
        return redirect("/login")
    user = User.query.get(session['user_id'])
    if not user.user_made_dish:
        flash("You can only comment on dishes you've made.", 'warning')
        return redirect('/meal_plans')
    form=CommentForm()
    if form.validate_on_submit():
        content=form.content.data
        new_comment=Comment(content=content)
        db.session.add(new_comment)
        db.session.commit()
        return redirect('/comments')
    return render_template('comment_form.html', form=form)

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