class Config(object):
    MYSQL_DATABASE_HOST = ''
    MYSQL_DATABASE_USER = ''
    MYSQL_DATABASE_PASSWORD = ''
    MYSQL_DATABASE_PORT = 0
    MYSQL_DATABASE_CONNECTOR = 'mysql+pymysql'

class TestConfig(Config):
    MYSQL_DATABASE_DB = ''
    DEVELOPMENT = True

class ProdConfig(Config):
    MYSQL_DATABASE_DB = ''
    DEVELOPMENT = False

class DevConfig(Config):
    MYSQL_DATABASE_DB = ''
    DEVELOPMENT = True
