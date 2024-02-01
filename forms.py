from wtforms_alchemy import model_form_factory
from wtforms_alchemy.fields import StringField, SelectField
from wtforms_components.fields.html5 import IntegerField, StringField
from wtforms import BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length
from wtforms_alchemy.validators import Unique
from flask_wtf import FlaskForm
from models import User, Meal, Comment, MealPlan, db

BaseModelForm = model_form_factory(FlaskForm)

DIET_CHOICES = [
    ('gluten_free', 'Gluten Free'),
    ('keto', 'Ketogenic'),
    ('vegetarian', 'Vegetarian'),
    ('lacto_vegetarian', 'Lacto-Vegetarian'),
    ('ovo_vegetarian', 'Ovo-Vegetarian'),
    ('vegan', 'Vegan'),
    ('pescetarian', 'Pescetarian'),
    ('paleo', 'Paleo'),
    ('primal', 'Primal'),
    ('low_fodmap', 'Low FODMAP'),
    ('whole30', 'Whole30')
]

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session
    
class MealForm(ModelForm):
    class Meta:
        model = Meal
    in_wishlist=BooleanField()
    user_made_dish=BooleanField()

class RegisterForm(ModelForm):
    class Meta:
        model = User

    username = StringField(validators=[Unique(User.username), InputRequired()])
    password = PasswordField(validators=[InputRequired()])
    email = StringField(validators=[Unique(User.email), InputRequired()])

class EditUserForm(ModelForm):
    class Meta:
        model=User
    username = StringField(validators=[Unique(User.username), InputRequired()])
    email = StringField(validators=[Unique(User.email), InputRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class MealPlanForm(FlaskForm):
        class Meta:
            model=MealPlan
        diet = SelectField('Diet', choices=DIET_CHOICES, validators=[DataRequired()])
        timeframe = SelectField('Timeframe', choices=[('day', 'Day'), ('week', 'Week')], validators=[DataRequired()])
        target_calories = IntegerField('Target Calories', validators=[DataRequired()])
        exclude = TextAreaField('Exclude')

class CommentForm(ModelForm):
    class Meta:
        model=Comment
    content=TextAreaField(validators=[InputRequired(), Length(max=255)])