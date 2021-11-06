import re
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class PreRegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=60)])
    submit = SubmitField("Send Email")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:  # if email exists in the User table
            raise ValidationError(
                "That email is used by another user. Please user a diffferent one."
            )


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:  # if user exists in the User table
            raise ValidationError("That username is taken. Please choose a diffferent one.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    zipcode = StringField("Zipcode")
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:  # if user exists in the User table
                raise ValidationError("That username is taken. Please choose a diffferent one.")

    def validate_zipcode(self, zipcode):
        valid_zip = re.search(r"^\d{5}$", zipcode.data)
        if not valid_zip or not weather_from_api(zipcode.data, "imperial"):
            raise ValidationError(
                "That doesn't look like a US zip code. Please try a different one."
            )


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Email")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:  # if email doesn't exist
            raise ValidationError(
                "There is no account with that email, you must register first."
            )


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
