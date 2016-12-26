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
    SECRET_KEY = "\xdb\x04\xb2S\xdf!n\x85F\x03\x13\xfe\xb9+\xab\x86\x82\xda'\xd1w\x1d\xacY"


config = {
    'default': DefaultConfig,
    'dev': DevConfig,
    'qa': QAConfig,
    'prod': ProdConfig
}
