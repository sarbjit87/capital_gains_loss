import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') #secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    CSV_UPLOAD = os.path.join(basedir, 'uploads')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_REFRESH_EACH_REQUEST = True
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

class TestConfig:
    SECRET_KEY = '13b8184b924cf6f8e31fdf3fdssdd3725' #secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'testapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    CSV_UPLOAD = os.path.join(basedir, 'uploads')
    WTF_CSRF_ENABLED = False
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    RECAPTCHA_PUBLIC_KEY = "your_key"
    RECAPTCHA_PRIVATE_KEY = "your_key"
