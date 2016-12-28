class DefaultConfig:
    """Default config class."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(DefaultConfig):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/users.db'
    SECRET_KEY = 'a very secret key'


class QAConfig(DefaultConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/users.db'
    SECRET_KEY = 'a very secret key'


class ProdConfig(DefaultConfig):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/userapi'
    SECRET_KEY = 'keep this key secret!'


config = {
    'default': DefaultConfig,
    'dev': DevConfig,
    'qa': QAConfig,
    'prod': ProdConfig
}
