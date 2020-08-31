import click
import random
from cli.commands.data import (
    statuses,
    generate_comments,
    generate_feedback
)
from sqlalchemy_utils import database_exists, create_database
from app.app import create_app
from app.extensions import db
from app.blueprints.base.functions import generate_id, generate_name, generate_private_key
from app.blueprints.api.models.user import User
from app.blueprints.api.models.domain import Domain
from app.blueprints.base.models.status import Status
from app.blueprints.base.models.feedback import Feedback
from app.blueprints.base.models.vote import Vote
from app.blueprints.base.models.comment import Comment

# Create an app context for the database connection.
app = create_app()
db.app = app


@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
def init(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    db.drop_all()

    db.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])

        if not database_exists(db_uri):
            create_database(db_uri)


@click.command()
def seed_users():
    """
    Seed the database with an initial api.

    :return: User instance
    """
    if User.find_by_identity(app.config['SEED_ADMIN_EMAIL']) is not None:
        return None

    admin = {
        'role': 'admin',
        'email': app.config['SEED_ADMIN_EMAIL'],
        'username': app.config['SEED_ADMIN_USERNAME'],
        'password': app.config['SEED_ADMIN_PASSWORD'],
        'name': 'Admin'
    }

    feedback = {
        'role': 'creator',
        'email': app.config['SEED_MEMBER_EMAIL'],
        'username': app.config['SEED_MEMBER_USERNAME'],
        'password': app.config['SEED_ADMIN_PASSWORD'],
        'domain': 'feedback',
        'name': 'Ricky'
    }

    User(**feedback).save()

    return User(**admin).save()


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
@click.pass_context
def reset(ctx, with_testdb):
    """
    Init and seed_users automatically.

    :param with_testdb: Create a test database
    :return: None
    """
    ctx.invoke(init, with_testdb=with_testdb)
    ctx.invoke(seed_users)

    return None


cli.add_command(init)
cli.add_command(seed_users)
cli.add_command(reset)