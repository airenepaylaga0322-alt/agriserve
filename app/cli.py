import click
from flask.cli import with_appcontext

from .extensions import db
from .models.user import User, Role


def register_commands(app):
    app.cli.add_command(init_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(seed_officer)


@click.command("init-db")
@with_appcontext
def init_db():
    """Create all database tables."""
    db.create_all()
    click.echo("Database tables created.")


@click.command("create-admin")
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--name", prompt="Full name", default="Administrator")
@with_appcontext
def create_admin(email, password, name):
    """Create an administrator account."""
    email = email.lower().strip()
    if User.query.filter_by(email=email).first():
        click.echo(f"User with email {email} already exists.")
        return
    user = User(email=email, full_name=name, role=Role.ADMIN)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Admin created: {email}")


@click.command("seed-officer")
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--name", prompt="Full name", default="Agricultural Officer")
@with_appcontext
def seed_officer(email, password, name):
    """Create an agricultural officer account."""
    email = email.lower().strip()
    if User.query.filter_by(email=email).first():
        click.echo(f"User with email {email} already exists.")
        return
    user = User(email=email, full_name=name, role=Role.OFFICER)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Officer created: {email}")