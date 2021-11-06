from flask.cli import FlaskGroup

from app import create_app, db
from app.models import User


app = create_app()
cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add(User(email="khiemnguyen@umass.edu"))
    db.session.commit()


if __name__ == "__main__":
    cli()
