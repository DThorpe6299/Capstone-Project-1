from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()

db = SQLAlchemy()

class MealPlan(db.Model):
    __tablename__ = 'meal_plans'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), primary_key=True)
    diet = db.Column(db.String(70), nullable=True)
    timeframe = db.Column(db.Enum('day', 'week'), nullable=False)
    target_calories = db.Column(db.Integer, nullable=False)
    exclude = db.Column(db.Text, nullable=True)

    
    user = db.relationship("User", backref='meal_plans')
    meal = db.relationship("Meal", backref='meal_plans')

class User(db.Model):
    """User."""
    @classmethod
    def register(cls, username, pwd):
        """Registering user with hashed password &return user."""
        hashed=bcrypt.generate_password_hash(pwd)
        hashed_utf8=hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8)
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct. Return user if valid; else return False."""

        u=User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False
        
    __tablename__='users'

    id=db.Column(db.Intger, primary_key=True, autoincrement=True)
    username=db.Column(db.String(50), unique=True, nullable=False)
    password=db.Column(db.String(50), nullable=False)
    email=db.Column(db.Text, nullable=False, unique=True)
    comment_id=db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    meal_plan_id=db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=False)
    meals = db.relationship('Meal', secondary='meal_plans', backref='users', lazy='dynamic')

class Meal(db.Model):
    """Meal model."""
    __tablename__='meals'
    id=db.Column(db.Intger, primary_key=True, autoincrement=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    in_wishlist=db.Column(db.Boolean, nullable=False, default=False)
    user_made_dish=db.Column(db.Boolean, nullable=False, default=False)
    users = db.relationship('User', secondary='meal_plans', backref='meals', lazy='dynamic')
    

class Comment(db.Model):
    """Comments model."""
    __tablename__='comments'
    id=db.Column(db.Intger, primary_key=True, autoincrement=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users=db.relationship('User')