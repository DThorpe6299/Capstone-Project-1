from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import traceback

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
            return None  
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct. Return user if valid; else return False."""

        u=User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False
        
    __tablename__='users'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(50), unique=True, nullable=False)
    password=db.Column(db.String(50), nullable=False)
    email=db.Column(db.Text, nullable=False, unique=True)
    meal_plan_id=db.Column(db.Integer, db.ForeignKey('meal_plans.id'), unique = True)
    #meals = db.relationship('Meal', secondary='meal_plans', backref='users', lazy='dynamic')

class Meal(db.Model):
    """Meal model."""
    __tablename__='meals'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    #user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    in_wishlist=db.Column(db.Boolean, nullable=False, default=False)
    user_made_dish=db.Column(db.Boolean, nullable=False, default=False)
    #users = db.relationship('User', secondary='meal_plans', backref='meals', lazy='dynamic')
    

class Comment(db.Model):
    """Comments model."""
    __tablename__='comments'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    users=db.relationship('User')

class MealPlan(db.Model):
    __tablename__ = 'meal_plans'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), primary_key=True)
    diet = db.Column(db.String(70), nullable=True)
    timeframe = db.Column(db.Enum('day', 'week', name='timeframe'), nullable=False)
    target_calories = db.Column(db.Integer, nullable=False)
    exclude = db.Column(db.Text, nullable=True)

    
    #user = db.relationship("User", backref='meal_plans')
    #meal = db.relationship("Meal", backref='meal_plans')