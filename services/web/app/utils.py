from flask import current_app, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Message

from app import mail


def serialize(content, valid_time=1800):
    s = Serializer(current_app.config["SECRET_KEY"], valid_time)
    return s.dumps(content).decode("utf-8")


def send_pre_register_email(email):
    # Serializer (secret_key, expiration_time(seconds))
    msg = Message(
        "Lunch With Friends Registration Email (valid for 30 minutes)",
        sender=("Lunch With Friends", "codergeorge01@gmail.com"),
        recipients=[email],
    )
    msg.body = f"""To create an account, visit the following link:
{url_for('users.register', token=serialize({'email': email}), _external=True)}

If you did not make this request, then simply ignore this email and no changes will be made.
"""
    # _external=True makes url_form return an absolute url (contains full domain) instead of relative one
    mail.send(msg)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Lunch With Friends Password Reset Request",
        sender=("Lunch With Friends", "codergeorge01@gmail.com"),
        recipients=[user.email],
    )
    msg.body = f"""To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, then simply ignore this email and no changes will be made.
"""
    # _external=True makes url_form return an absolute url (contains full domain) instead of relative one
    mail.send(msg)
