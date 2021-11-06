from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    session,
)
from flask_login import current_user, login_user, logout_user, login_required

from app import db, bcrypt, login_manager
from app.models import User
from app.utils import send_pre_register_email, Serializer, send_reset_email
from app.forms import (
    PreRegisterForm,
    RegisterForm,
    LoginForm,
    RequestResetForm,
    # UpdateAccountForm,
    ResetPasswordForm,
)

main_bp = Blueprint("main", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/pre_register", methods=["GET", "POST"])
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
        return redirect(url_for("main.pre_register"))
    return render_template("pre_register.html", title="Register", form=form)


@main_bp.route("/register/<token>", methods=["GET", "POST"])
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


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)  # remember me is a true/false value
            next_page = request.args.get(
                "next"
            )  # user get('next') instead of ['next'] because it returns none if key does not exist
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", title="Login", form=form)


@main_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


# @main_bp.route("/account", methods=["GET", "POST"])
# @login_required
# def account():
#     form = UpdateAccountForm()
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         db.session.commit()
#         flash("Your account has been updated!", "success")
#         return redirect(url_for("users.account"))
#     elif request.method == "GET":
#         form.username.data = current_user.username
#     return render_template("account.html", title="Account", form=form)


@main_bp.route("/reset_password", methods=["GET", "POST"])
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


@main_bp.route("/reset_password/<token>", methods=["GET", "POST"])
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
