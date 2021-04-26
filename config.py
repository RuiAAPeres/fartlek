import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SANDOX = False


class ProductionConfig(Config):
    SANDOX = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SANDOX = True
