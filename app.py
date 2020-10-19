from modules_and_libraries import *
import os


app = Flask(__name__)

authorizations = {
    'Authorization': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

#initializing CORS
cors = CORS(app, resources={
    r"/*":{
        "origins":"*"
    }
})

# Initialization of API
api = Api(app=app, version="2.0",title="mysale-backend",description="mysale app of backend",authorizations=authorizations,security='Authorization', errors=errors)

# configure settings
#Database server
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SWAGGER_UI_JSONEDITOR'] = config.SWAGGER_UI_JSONEDITOR
#JWT
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_HEADER_NAME'] = config.JWT_HEADER_NAME
app.config['JWT_HEADER_TYPE'] = config.JWT_HEADER_TYPE
#CORS Header
app.config['CORS_HEADERS'] = config.CORS_HEADER

#Mail Server
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = config.MAIL_USE_SSL
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER
mail = Mail(app)

bcrypt = Bcrypt(app=app)
jwt = JWTManager(app=app)
db = SQLAlchemy(app=app)

#namespace
ns_auth = api.namespace('auth', description='authorization')
ns_users = api.namespace('users', description='users')
ns_category = api.namespace('category', description='Categories')
ns_vendor = api.namespace('vendor', description='Vendors')

# fields
register = api.model('REGISTER', {
    'first_name': fields.String(required=True, example='first_name'),
    'last_name': fields.String(required=True, example='last_name'),
    'email': fields.String(required=True, example='email@domain.com'),
    'password': fields.String(required=True, example='password'),
    'role': fields.String(required=True, example='admin/user')
})

login = api.model('LOGIN', {
    'email': fields.String(required=True, example='email@domain.com'),
    'password': fields.String(required=True, example='password')
})

forgot = api.model('FORGOT', {
    'email': fields.String(required=True, example='email@domain.com')
})

reset = api.model('RESET', {
    'new_password': fields.String(required=True, example='new_password'),
    'confirm_password': fields.String(required=True, example='re_type_new_password')
})

update_user = api.model('UPDATE USER',{
    'first_name': fields.String(required=True, example='first_name'),
    'last_name': fields.String(required=True, example='last_name'),
    'email': fields.String(required=True, example='email@domain.com'),
    'role': fields.String(required=True, example='admin/user')
})

category = api.model('CATEGORY', {
    'name': fields.String(required=True, example='category_name'),
    'image_url': fields.String(example='default.jpg'),
    'description': fields.String(required=True),
    'order': fields.String(required=True)
})
 
vendor = api.model('VENDOR', {
    'name': fields.String(required=True, example='category_name'),
    'image_url': fields.String(example='default.jpg'),
    'description': fields.String(required=True),
    'order': fields.String(required=True)
})


if __name__ == '__main__':
    app.run(debug=True)
    