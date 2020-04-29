import pytest
from capital_gains_loss import create_app, db, bcrypt, login_manager
from capital_gains_loss.config import TestConfig
from capital_gains_loss.models import User, Transaction
from os import unlink

@pytest.fixture(scope='session')
def new_user():
    user = User(username='user1',email='user1@example.com',password='Password1!')
    return user


@pytest.fixture(scope='session')
def test_client():
    flask_app = create_app(TestConfig)

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='session')
def init_database():

    # Cleanup the database from previous runs and re-create it
    db.drop_all()
    db.create_all()

    hashed_password = bcrypt.generate_password_hash("Password1!").decode('utf-8')

    # Insert Users in the database
    user1 = User(username='user1',email='user1@example.com',password=hashed_password)
    user2 = User(username='user2',email='user2@example.com',password=hashed_password)
    db.session.add(user1)
    db.session.add(user2)

    db.session.commit()
    yield db
    #db.drop_all()

@pytest.fixture(scope='session')
def model_access():
    yield Transaction

@pytest.fixture(scope='session')
def test_with_authenticated_user(test_client):
    @login_manager.request_loader
    def load_user_from_request(request):
        return User.query.filter_by(username='user2').first()
