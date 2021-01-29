from unittest import TestCase

from app import app
from models import db, User, Feedback

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class FlaskTestCase(TestCase):
    """Tests for routes."""

    def setUp(self):
        """Add sample users."""

        User.query.delete()

        u1 = User.register(username="test1", password="test1",
                           first_name="tester", last_name='testerson', email="test@test.com")
        u2 = User(username="admin", password="admin", email="admin@admin.com",
                  first_name="Administrator", last_name="Admin", is_admin=True)
        db.session.add_all([u1, u2])
        db.session.commit()

        self.user_id = u1.id
        self.username = u1.username

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_home_page(self):
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="title">Home Page</h1>', html)

    def test_404_page(self):
        with app.test_client() as client:
            resp = client.get("/notalink")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('<h1 class="title">404 Not Found</h1>', html)

    def test_401_page(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['username'] = self.username
            resp = client.get("/users/admin")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn('<h1 class="title">401 Unauthorized</h1>', html)

    def test_admin(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['is_admin'] = True
            resp = client.get("/users/test1")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<h2 class="subtitle">Information for User: test1</h2>', html)

    def test_login_render(self):
        with app.test_client() as client:
            resp = client.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="title">Login</h1>', html)
            self.assertIn(
                '<label class="label is-small" for="username">Username</label>', html)
            self.assertIn(
                '<label class="label is-small" for="password">Password</label>', html)

    def test_login(self):
        with app.test_client() as client:
            d = {"username": "test1", "password": "test1"}
            resp = client.post("/login", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<h2 class="subtitle">Information for User: test1</h2>', html)
            self.assertIn(
                '<p class="title is-4">Username: test1</p>', html)
            self.assertIn(
                '<p class="subtitle is-6 mt-3"><b>Full Name:</b> tester testerson</p>', html)

    def test_register_render(self):
        with app.test_client() as client:
            resp = client.get("/register")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="title">Register</h1>', html)
            self.assertIn(
                '<label class="label is-small" for="username">Username</label>', html)
            self.assertIn(
                '<label class="label is-small" for="password">Password</label>', html)

    def test_register(self):
        with app.test_client() as client:
            d = {"username": "test2", "password": "test2", "email": "testing@gmail.com",
                 "first_name": "testy", "last_name": "testman"}
            resp = client.post("/register", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<h2 class="subtitle">Information for User: test2</h2>', html)
            self.assertIn(
                '<p class="title is-4">Username: test2</p>', html)
            self.assertIn(
                '<p class="subtitle is-6 mt-3"><b>Full Name:</b> testy testman</p>', html)

    def test_delete_user(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['username'] = 'test1'
            resp = client.get("/users/test1/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="title">Login</h1>', html)
            self.assertIn(
                '<label class="label is-small" for="username">Username</label>', html)
            self.assertIn(
                '<label class="label is-small" for="password">Password</label>', html)
