import os
import pytest

from app import app as _app, db as _db, User


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = _app

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    conn_str = app.config.get('SQLALCHEMY_DATABASE_URI')
    db_path = conn_str.replace('sqlite:///', '')

    if os.path.exists(db_path):
        os.unlink(db_path)

    def teardown():
        _db.drop_all()
        os.unlink(db_path)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='session')
def session(db, request):
    """Creates a new database session for a test and add test data."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)

    _user = User(username='foo', email='foo@gmail.com')
    _user.hash_password('password')

    session.add(_user)

    _user2 = User(username='bar', email='bar@gmail.com')
    _user2.hash_password('password')

    session.add(_user2)

    session.commit()

    return session


@pytest.fixture(scope="session")
def user(session):
    return session.query(User).filter_by(id=1).first()


@pytest.fixture(scope="session")
def users(session):
    return session.query(User).all()


@pytest.fixture(scope="session")
def test_client(app):
    return app.test_client()
