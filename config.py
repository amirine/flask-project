import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    # Secret project key variable
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    POSTS_PER_PAGE = 3

    # Database variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Variables for sending errors by email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['zhuk.irina.2000@gmail.com']
