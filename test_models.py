from unittest import TestCase

from app import app
from models import db, User, Feedback

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Tests for model for Users class."""

    def setUp(self):
        """Clean up any existing users."""
        Feedback.query.delete()
        User.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_create_user(self):
        u = User.register(username="test1", password="test1",
                          first_name="tester", last_name='testerson', email="test@test.com")
        db.session.add(u)
        db.session.commit()

        self.assertEqual(u.username, "test1")
        self.assertEqual(u.full_name, "tester testerson")

    def test_edit_user(self):
        u = User.register(username="test1", password="test1",
                          first_name="tester", last_name='testerson', email="test@test.com")
        db.session.add(u)
        db.session.commit()
        u.is_admin = True
        db.session.commit()

        self.assertEqual(u.username, "test1")
        self.assertEqual(u.full_name, "tester testerson")
        self.assertTrue(u.is_admin)

    def test_authenticate(self):
        r = User.register(username="test1", password="test1",
                          first_name="tester", last_name='testerson', email="test@test.com")
        db.session.add(r)
        db.session.commit()
        u = User.authenticate(username="test1", password="test1")

        self.assertEqual(r.username, "test1")
        self.assertEqual(r.full_name, "tester testerson")
        self.assertEqual(u.username, "test1")
        self.assertEqual(u.full_name, "tester testerson")


class FeedbackModelTestCase(TestCase):
    """Tests for model for feedback class."""

    def setUp(self):
        """Clean up any existing feedback."""

        Feedback.query.delete()
        User.query.delete()
        r = User.register(username="test1", password="test1",
                          first_name="tester", last_name='testerson', email="test@test.com")
        db.session.add(r)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_create_feedback(self):
        f = Feedback(title='Test Feedback',
                     content='Here is some test text', username='test1')

        db.session.add(f)
        db.session.commit()

        self.assertEqual(f.title, 'Test Feedback')
        self.assertEqual(f.content, 'Here is some test text')

    def test_edit_feedback(self):
        f = Feedback(title='Test Feedback',
                     content='Here is some test text', username='test1')

        db.session.add(f)
        db.session.commit()

        f.title = "Edited Feedback"
        f.content = "Here is some edit text"

        self.assertEqual(f.title, 'Edited Feedback')
        self.assertEqual(f.content, 'Here is some edit text')
