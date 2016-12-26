from app import verify_password, validate_token, User
import json
from base64 import b64encode


def auth_headers(username, password):
    username_password = "%s:%s" % (username, password)
    headers = {
        'Authorization': 'Basic %s' % b64encode(username_password.encode()).decode("ascii")
    }
    return headers


def test_verify_password_callback(test_client, app, user):
    username = user.username
    password = 'password'
    token = user.generate_auth_token()

    # test username, password, token as auth headers
    with app.test_request_context():
        assert verify_password(username, password) is True
        assert verify_password(token) is True
        assert verify_password('blah', 'blah') is False
        assert verify_password('12345') is False
        assert verify_password() is False

    # test token as parameter
    uri = "/api/v1/users?token={}".format(token.decode('utf-8'))
    with app.test_request_context(uri):
        assert verify_password() is True


def test_get_auth_token(test_client, user):
    uri = '/api/v1/token'
    headers = auth_headers(user.username, 'password')
    resp = test_client.get(uri, headers=headers, follow_redirects=True)
    data = json.loads(resp.data.decode('utf-8'))
    assert 'token' in data


def test_validate_token(user, app):
    token = user.generate_auth_token()
    with app.test_request_context():
        resp = validate_token(token)
        data = json.loads(resp.data.decode('utf-8'))
        assert 'is_valid' in data
        assert data.get('is_valid') is True


class TestUserAPI:

    def create_user(self, test_client, user, new_user,
                    auth_password='password', password='password'):
        uri = '/api/v1/users/'
        headers = auth_headers(user.username, auth_password)
        resp = test_client.post(uri,
                                query_string=dict(username=new_user.username,
                                                  password=password,
                                                  email=new_user.email),
                                headers=headers,
                                follow_redirects=True)
        return resp

    def get_user(self, test_client, username, auth_username='foo',
                 auth_password='password'):
        uri = '/api/v1/users/%s' % username
        headers = auth_headers(auth_username, auth_password)
        resp = test_client.get(uri, headers=headers, follow_redirects=True)
        return resp

    def test_getting_a_user(self, test_client, user):
        resp = self.get_user(test_client, user.username)

        assert resp.status_code == 200
        data = json.loads(resp.data.decode('utf-8'))

        assert data['email'] == user.email
        assert data['username'] == user.username
        assert data['id'] == user.id

    def test_getting_users(self, test_client, users):
        uri = '/api/v1/users/'
        headers = auth_headers(users[0].username, 'password')
        resp = test_client.get(uri, headers=headers, follow_redirects=True)

        assert resp.status_code == 200

        data = json.loads(resp.data.decode('utf-8'))

        assert len(data) == len(users)

        for i, user in enumerate(data):
            assert data[i]['email'] == users[i].email
            assert data[i]['username'] == users[i].username
            assert data[i]['id'] == users[i].id

    def test_creating_a_user(self, test_client, user):
        new_user = User(username='new',
                        email='new@gmail.com')
        new_password = 'password'
        uri = '/api/v1/users/'
        headers = auth_headers(user.username, new_password)
        resp = test_client.post(uri,
                                query_string=dict(username=new_user.username,
                                                  password=new_password,
                                                  email=new_user.email),
                                headers=headers,
                                follow_redirects=True)

        assert resp.status_code == 201

        data = json.loads(resp.data.decode('utf-8'))

        assert data['email'] == new_user.email
        assert data['username'] == new_user.username

    def test_updating_a_user(self, test_client, user):
        username = 'new'  # created from previous test
        uri = '/api/v1/users/%s' % username
        headers = auth_headers(user.username, 'password')
        new_username = 'updated'
        new_email = 'updated@gmail.com'
        new_password = 'new_password'
        resp = test_client.put(uri,
                               query_string=dict(new_username=new_username,
                                                 new_email=new_email,
                                                 new_password=new_password),
                               headers=headers, follow_redirects=True)

        assert resp.status_code == 200

        resp = self.get_user(test_client, new_username)

        data = json.loads(resp.data.decode('utf-8'))

        assert data['email'] == new_email
        assert data['username'] == new_username

    def test_deleting_a_user(self, test_client, user):
        username = 'updated'  # from previous test
        uri = '/api/v1/users/%s' % username
        headers = auth_headers(user.username, 'password')

        # delete the user
        resp = test_client.delete(uri, headers=headers)
        assert resp.status_code == 200

        # test that the user is actually deleted
        resp = self.get_user(test_client, username)
        assert resp.status_code == 404
