class Config(object):
    MYSQL_DATABASE_HOST = ''
    MYSQL_DATABASE_USER = ''
    MYSQL_DATABASE_PASSWORD = ''
    MYSQL_DATABASE_PORT = 0
    MYSQL_DATABASE_CONNECTOR = 'mysql+pymysql'
    DEFAULT_NONE_IMAGE = 'img/defaults/NONE.jpg'
    S3_BUCKET_NAME = ''
    IMAGE_SOURCE_PATH = ''
    S3_ACCESS_KEY = ''
    S3_SECRET_KEY = ''

class TestConfig(Config):
    MYSQL_DATABASE_DB = ''
    DEVELOPMENT = True

class ProdConfig(Config):
    MYSQL_DATABASE_DB = ''
    DEVELOPMENT = False

class DevConfig(Config):
    MYSQL_DATABASE_DB = ''
    DEVELOPMENT = True
