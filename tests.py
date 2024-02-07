from unittest import TestCase
from app import app
from models import db, User, Meal, MealPlan, Comment

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///meal_plan_db'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

with app.app_context():
    db.drop_all()
    db.create_all()


class TestApp(TestCase):
    def test_index_redirect(self):
            response = self.app.get('/')
            self.assertEqual(response.status_code, 302)

    def test_login_page(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_successful_login(self):
        response = self.app.post('/login', data=dict(
            username='test_user',
            password='test_password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_unsuccessful_login(self):
        response = self.app.post('/login', data=dict(
            username='test_user',
            password='wrong_password'
        ), follow_redirects=True)
        self.assertIn("Incorrect username/password", response.data)

