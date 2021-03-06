import os
from dotenv import load_dotenv

load_dotenv()

# SQLALCHEMY SETTINGS
#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'] = 'sqlite:///database.db'
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_TRACK_MODIFICATIONS=True
SECRET_KEY=os.environ['SECRET_KEY']

# CORS SETTINGS
CORS_HEADER = os.environ['CORS_HEADER']

#JWT SETTINGS

JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_HEADER_TYPE = os.environ['JWT_HEADER_TYPE']
JWT_HEADER_NAME = os.environ['JWT_HEADER_NAME']

# MAIL SETTINGS
MAIL_SERVER = os.environ['MAIL_SERVER']
MAIL_USERNAME = os.environ['MAIL_USERNAME']
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
MAIL_DEFAULT_SENDER = os.environ['MAIL_DEFAULT_SENDER']
MAIL_PORT = os.environ['MAIL_PORT']
MAIL_USE_TLS = False
MAIL_USE_SSL = True

# SWAGGER SETTINGS
SWAGGER_UI_JSONEDITOR = True
