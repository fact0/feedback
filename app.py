from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError, DataError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['UPLOADED_IMAGES_DEST'] = '/static/media'
debug = DebugToolbarExtension(app)
images = UploadSet('images', IMAGES)
configure_uploads(app, (images,))

connect_db(app)
db.create_all()


@app.route('/')
def home_page():
    """Renders home page"""

    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""
    error = '404 Not Found'
    text = "Sorry looks like we can't find the page you are looking for"

    return render_template('error.html', error=error, text=text), 404


@app.errorhandler(401)
def page_unauthorized(e):
    """Show 401 Unauthorized page."""
    error = '401 Unauthorized'
    text = "You are Unauthorized to view that page, please login and try again"
    return render_template('error.html', error=error, text=text), 401


@app.route('/users/<username>')
def render_user_details(username):
    authorize(username)

    user = User.query.filter_by(username=username).first()
    return render_template('user.html', user=user)


@app.route('/users/<username>/delete')
def delete_user(username):
    authorize(username)

    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    flash('User deleted successfully!', 'success')
    return redirect("/login")


@app.route('/register', methods=["GET", "POST"])
def register_user():
    if "username" in session:
        flash("You are already registered", "danger")
        return redirect(f"/users/{session['username']}")
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        new_user = User.register(
            username, password, first_name, last_name, email)
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username/Email is already taken")
            return render_template('register.html', form=form)

        session['username'] = new_user.username

        flash('Welcome! Account created successfully!', 'success')
        return redirect(f'/users/{new_user.username}')
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login_user():
    if "username" in session:
        flash("You are already logged in", "danger")
        return redirect(f"/users/{session['username']}")
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}!", "success")
            session["username"] = user.username
            if user.is_admin:
                session["is_admin"] = True
            else:
                session["is_admin"] = False
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop("username")
    if "is_admin" in session:
        session.pop("is_admin")
    flash('Successfully logged out', 'success')
    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_user_feedback(username):
    authorize(username)
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_feedback = Feedback(
            title=title, content=content, username=username)
        db.session.add(new_feedback)

        try:
            db.session.commit()
        except DataError:
            form.title.errors.append(
                "Title must be shorter than 100 characters")
            return render_template('feedback.html', form=form)

        flash('Feedback created successfully!', 'success')
        return redirect(f'/users/{new_feedback.username}')
    else:
        return render_template('feedback.html', form=form, text="create a new")


@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_user_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    username = feedback.username
    authorize(username)

    db.session.delete(feedback)
    db.session.commit()

    flash('Feedback deleted successfully!', 'success')
    return redirect(f"/users/{feedback.username}")


@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def update_user_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    username = feedback.username
    authorize(username)
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        flash('Feedback updated successfully!', 'success')
        return redirect(f"/users/{username}")
    else:
        return render_template('feedback.html', form=form, text="edit a")


def authorize(username):
    if "is_admin" not in session or session["is_admin"] == False:
        if "username" not in session or username != session['username']:
            flash("Please login first", "danger")
            raise Unauthorized()
