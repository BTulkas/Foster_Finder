import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_key_string"

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://fosterfinder:1212@localhost:3306/foster_finder'
    #   'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['btulkas@gmail.com']

    rc_key = open('recaptcha_keys.txt')
    RECAPTCHA_PRIVATE_KEY = rc_key.readline() if rc_key else os.environ.get('RC_KEY')
    rc_key.close()
    RECAPTCHA_PUBLIC_KEY = '6LcKfcwZAAAAABKb0jwA-Z0-6Ad4X3WBPKpv9lth'
