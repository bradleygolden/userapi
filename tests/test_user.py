from app import User


class TestUser:

    def test_verify_password(self, user):
        assert user.verify_password('password') is True
        assert user.verify_password('blah') is False

    def test_verify_auth_token(self, user):
        token = user.generate_auth_token()
        assert isinstance(User.verify_auth_token(token), User) is True
        assert isinstance(User.verify_auth_token('blah'), User) is False
