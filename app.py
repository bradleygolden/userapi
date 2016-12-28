"""This is a simple user api for creating and storing users."""

import os
from flask import Flask, request, jsonify, abort, g, Blueprint
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from config import config
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# setup flask
app = Flask(__name__, static_url_path='')
config_obj = config[os.getenv('FLASK_ENV') or config.get('default')]
app.config.from_object(config_obj)

# flask extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth()
ma = Marshmallow(app)

# create blueprints
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')


# define a user model class to store users
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String)
    password_hash = db.Column(db.String)
    avatar = db.Column(db.String)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


# define user schema for serialization
class UserSchema(ma.ModelSchema):

    class Meta:
        model = User
        exclude = ("password_hash",)


# schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@auth.verify_password
def verify_password(username_or_token=None, password=None):
    """Callback for verifying a username and password or token."""
    # first try to authenticate by token in header or url
    verify_token_in_header = None
    if username_or_token:
        verify_token_in_header = User.verify_auth_token(username_or_token)

    verify_token_as_param = None
    if not username_or_token:
        token = request.args.get('token', '')
        verify_token_as_param = User.verify_auth_token(token)

    user = verify_token_in_header or verify_token_as_param
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@api_v1.route('/token')
@auth.login_required
def get_auth_token():
    """A route to get an auth token for a user."""
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@api_v1.route('/validate/token/<string:token>')
def validate_token(token):
    """A route to validate a user token.

    Optional: You can also validate a username and token together. Simply
              provide the username as a parameter."""
    user = User.verify_auth_token(token)
    username = request.args.get('username')

    valid = False
    if user is not None and username is not None and user.username == username:
        valid = True
    elif user is not None and username is None:
        valid = True
    else:
        valid = False

    return jsonify({'is_valid': valid})


class UserAPI(MethodView):

    decorators = [auth.login_required]

    def get(self, username=None):
        """Get a user or users."""
        if username:  # /users/username
            user = User.query.filter_by(username=username).first_or_404()
            serialized_user = user_schema.dump(user).data
            return jsonify(serialized_user), 200
        else:  # /users
            users = User.query.all()
            serialized_users = users_schema.dump(users).data
            return jsonify(serialized_users), 200

    def post(self):
        """Create a new user."""
        password = request.args.get('password')
        username = request.args.get('username')
        email = request.args.get('email')
        if username is None or password is None:
            abort(400)  # missing arguments
        if User.query.filter_by(username=username).first() is not None:
            abort(400)  # existing user
        user = User(username=username, email=email)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        serialized_user = user_schema.dump(user).data
        return jsonify(serialized_user), 201

    def put(self, username):
        """Update a user."""
        new_username = request.args.get('new_username')
        new_password = request.args.get('new_password')
        new_email = request.args.get('new_email')
        user = User.query.filter_by(username=username).first_or_404()
        if new_username and new_username != username:
            user.username = new_username
        if new_email:
            user.email = new_email
        if new_password:
            user.hash_password(new_password)  # update password
        db.session.commit()
        serialized_user = user_schema.dump(user).data
        return jsonify(serialized_user), 200

    def delete(self, username):
        """Delete a user."""
        user = User.query.filter_by(username=username).first_or_404()
        db.session.delete(user)
        db.session.commit()
        return jsonify({}), 200


# add urls to views
user_view = UserAPI.as_view('user_api')
api_v1.add_url_rule('/users/', view_func=user_view,
                    methods=['GET', 'POST'])
api_v1.add_url_rule('/users/<string:username>', view_func=user_view,
                    methods=['GET', 'PUT', 'DELETE'])

# register_blueprints
app.register_blueprint(api_v1)


def create_user(username, password):
    user = User(username=username)
    if not User.query.filter_by(username=user.username).first():
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
