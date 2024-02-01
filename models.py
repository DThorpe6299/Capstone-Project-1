from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import traceback
from enum import Enum

bcrypt=Bcrypt()

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)



class User(db.Model):
    """User."""
    @classmethod
    def register(cls, username, pwd, email):
        """Registering user with hashed password &return user."""
        try:
            hashed = bcrypt.generate_password_hash(pwd)
            hashed_utf8 = hashed.decode("utf8")
            new_user = cls(username=username, password=hashed_utf8, email=email)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            
            traceback.print_exc()
            db.session.rollback()
            return e  
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct. Return user if valid; else return False."""

        user = cls.query.filter_by(username=username).first()
        print(f"User found: {user}")
        if user:
            password_check = bcrypt.check_password_hash(user.password, pwd)
            print(f"Password check: {password_check}")
            if password_check:
                return user
    
        return None
        
    __tablename__='users'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(255), unique=True, nullable=False)
    password=db.Column(db.String(255), nullable=False)
    email=db.Column(db.Text, nullable=False, unique=True)
    meal_plans = db.relationship('MealPlan', backref='user', lazy=True)
    #meals = db.relationship('Meal', secondary='meal_plans', backref='users', lazy='dynamic')

class DaysOfWeek(Enum):
    Monday = 'Monday'
    Tuesday = 'Tuesday'
    Wednesday = 'Wednesday'
    Thursday = 'Thursday'
    Friday = 'Friday'
    Saturday = 'Saturday'
    Sunday = 'Sunday'
    

class Meal(db.Model):
    """Meal model."""
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    in_wishlist = db.Column(db.Boolean, nullable=False, default=False)
    user_made_dish = db.Column(db.Boolean, nullable=False, default=False)
    day_of_week = db.Column(db.Enum(DaysOfWeek), nullable=True)
    title=db.Column(db.String(255), nullable=False, default='Unknown Title')
    source_url = db.Column(db.String(255), nullable=True)
    ready_in_minutes = db.Column(db.Integer, nullable=True)
    servings = db.Column(db.Integer, nullable=True)
    created_on= db.Column(db.DateTime, server_default=db.func.now())
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=True)
    
    

class Comment(db.Model):
    """Comments model."""
    __tablename__='comments'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    meal_id=db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    content=db.Column(db.String(255), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user=db.relationship('User', backref='comments')

class MealPlan(db.Model):
    __tablename__ = 'meal_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'))
    diet = db.Column(db.String(70), nullable=True)
    timeframe = db.Column(db.Enum('day', 'week', name='timeframe'), nullable=False)
    target_calories = db.Column(db.Integer, nullable=False)
    exclude = db.Column(db.Text, nullable=True)
    calories = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    created_on= db.Column(db.DateTime, server_default=db.func.now())

    meals = db.relationship('Meal', backref='meal_plan', cascade='all,delete', passive_deletes=True, foreign_keys="[MealPlan.meal_id]")


    
    #user = db.relationship("User", backref='meal_plans')
    #meal = db.relationship("Meal", backref='meal_plans')