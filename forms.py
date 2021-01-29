from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES
from wtforms.validators import InputRequired, Optional, URL, NumberRange, Length, Email
from wtforms import FloatField, BooleanField, IntegerField, RadioField, SelectField, TextAreaField, StringField, PasswordField


class MyInputRequired(InputRequired):
    field_flags = ()


class UserForm(FlaskForm):
    """Form for adding users"""

    username = StringField("Username", validators=[
        MyInputRequired(message="Username cannot be blank")])
    password = PasswordField("Password", validators=[
        MyInputRequired(message="Password cannot be blank")])
    first_name = StringField("First Name", validators=[
        MyInputRequired(message="First Name cannot be blank")])
    last_name = StringField("Last Name", validators=[
        MyInputRequired(message="Last Name cannot be blank")])
    email = StringField("Email", validators=[Email(),
                                             MyInputRequired(message="Email cannot be blank")])


class LoginForm(FlaskForm):
    """Form for loggining in"""

    username = StringField("Username", validators=[
        MyInputRequired(message="Username cannot be blank")])
    password = PasswordField("Password", validators=[
        MyInputRequired(message="Password cannot be blank")])


class FeedbackForm(FlaskForm):
    """Form for creating feedback posts"""

    title = StringField("Title", validators=[
        MyInputRequired(message="Title cannot be blank")])
    content = TextAreaField("Feedback Content", validators=[
        MyInputRequired(message="Content cannot be blank")])
