from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    from .views.main import main_bp

    app.register_blueprint(main_bp)

    return app
