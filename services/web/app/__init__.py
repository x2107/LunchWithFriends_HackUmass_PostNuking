import os
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    Blueprint,
    current_app,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Mail
from flask_bcrypt import Bcrypt

# from app.models import User
from app.utils import send_pre_register_email, Serializer, send_reset_email
from app.forms import (
    PreRegisterForm,
    RegisterForm,
    LoginForm,
    RequestResetForm,
    UpdateAccountForm,
    ResetPasswordForm,
)


app = Flask(__name__)
app.config.from_object("app.config.Config")
db = SQLAlchemy(app)
mail = Mail(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard.html")


@app.route("/pre_register", methods=["GET", "POST"])
def pre_register():
    # if current user is registered, redirect him to home
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = PreRegisterForm()
    if form.validate_on_submit():
        send_pre_register_email(form.email.data)
        flash(
            "A confirmation email has been sent to your account, please follow link there to complete registration",
            "info",
        )
        return redirect(url_for("users.pre_register"))
    return render_template("pre_register.html", title="Register", form=form)


@app.route("/register/<token>", methods=["GET", "POST"])
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    # decode token and try to get email
    s = Serializer(current_app.config["SECRET_KEY"])
    email = None
    try:
        email = s.loads(token)["email"]
    except:
        pass
    if email is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.pre_register"))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to login.", "success")
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.zipcode == "none":
                # None needs to be added to avoid keyerror
                session.pop("zipcode", None)
            else:
                session["zipcode"] = user.zipcode
            login_user(user, remember=form.remember.data)  # remember me is a true/false value
            next_page = request.args.get(
                "next"
            )  # user get('next') instead of ['next'] because it returns none if key does not exist
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    session.pop("zipcode", None)
    return redirect(url_for("main.home"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.zipcode = form.zipcode.data
        db.session.commit()
        # have to update zipcode in session (because it is stored in cookie)
        session["zipcode"] = form.zipcode.data
        flash("Your account has been updated!", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.zipcode.data = current_user.zipcode
    return render_template("account.html", title="Account", form=form)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset the password.", "info")
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)  # method returns a user if token is correct
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.add(user)
        db.session.commit()
        flash("Your password has been updated! You are now able to login.", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
