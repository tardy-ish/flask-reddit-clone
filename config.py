class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = '69420'

    db_username = 'postgres'
    db_password = 'daksh1234'
    db_host     = 'localhost'
    db_name     = 'flask-reddit'


    SQLALCHEMY_DATABASE_URI = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True