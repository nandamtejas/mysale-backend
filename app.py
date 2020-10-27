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

choices = list(range(1,25))

# parsing the parameters
pagination = RequestParser(bundle_errors=True)
pagination.add_argument("page", type=positive, required=False, default=1)
pagination.add_argument("per_page", type=positive, required=False, choices=choices, default=10)


#namespace
ns_auth = api.namespace('auth', description='authorization')
ns_users = api.namespace('users', description='users')
ns_category = api.namespace('category', description='Categories')
ns_vendor = api.namespace('vendor', description='Vendors')
ns_deals = api.namespace('deals', description='deals')
ns_user_cat_map = api.namespace('user_categories', description='User_Categories')
ns_user_vend_map = api.namespace('user_vendors', description='User-Vendors')
ns_user_deals_map = api.namespace('user_deals', description='User-Deals')

# fields
register = api.model('REGISTER', {
    'first_name': fields.String(required=True, example='first_name'),
    'last_name': fields.String(required=True, example='last_name'),
    'email': fields.String(required=True, example='email@domain.com'),
    'password': fields.String(required=True, example='password')
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
    'name': fields.String(required=True, example='vendor_name'),
    'image_url': fields.String(example='default.jpg'),
    'description': fields.String(required=True),
    'order': fields.String(required=True)
})

deals = api.model("DEALS", {
    'name': fields.String(required=True, example='deal_name'),
    'vendor_id': fields.Integer(requierd=True, example=1),
    'image_url': fields.String(example='default.jpg'),
    'start_date': fields.String(required=True, example='DD-MM-YYYY HH:mm AM'),
    'end_date': fields.String(required=True, example='DD-MM-YYYY HH:mm AM')
})

deal_tags = api.model("DEAL_TAGS", {
    'name': fields.String(required=True, example='deal_tag_name'),
    'category_id': fields.Integer(required=True, example=1)
})

user_cat = api.model("USER_CATEGORY", {
    'category_id': fields.Integer(required=True, example=1, description='category id'),
    'is_deleted': fields.Boolean(required=True, example=False)
})

user_ven = api.model("USER_VENDOR", {
    'vendor_id': fields.Integer(required=True, example=1, description='vendor id'),
    'is_deleted': fields.Boolean(required=True, example=False)
})

user_deal = api.model("USER_DEAL", {
    'deal_id': fields.Integer(required=True, example=1, description='deals id'),
    'is_deleted': fields.Boolean(required=True, example=False)
})

user_category_preferences = api.model("USER_CATEGORY_PREFERENCES",{
    'user_category_preferences': fields.List(fields.Nested(user_cat, skip_none=True))
})

user_vendor_preference = api.model("USER_VENDOR_PREFERENCES", {
    'user_vendor_preferences': fields.List(fields.Nested(user_ven, skip_none=True))
})

user_deal_preference = api.model("USER_DEAL_PREFERENCES", {
    'user_deal_preferences': fields.List(fields.Nested(user_deal, skip_none=True))
})

# error handlers for jwt

@api.errorhandler(NoAuthorizationError)
def handle_auth_error(e):
    return {'message': str(e)}, 401


@api.errorhandler(CSRFError)
def handle_auth_error(e):
    return {'message': str(e)}, 401


@api.errorhandler(ExpiredSignatureError)
def handle_expired_error(e):
    return {'message': 'Token has expired'}, 401


@api.errorhandler(InvalidHeaderError)
def handle_invalid_header_error(e):
    return {'message': str(e)}, 422


@api.errorhandler(InvalidTokenError)
def handle_invalid_token_error(e):
    return {'message': str(e)}, 422


@api.errorhandler(JWTDecodeError)
def handle_jwt_decode_error(e):
    return {'message': str(e)}, 422


@api.errorhandler(WrongTokenError)
def handle_wrong_token_error(e):
    return {'message': str(e)}, 422


@api.errorhandler(RevokedTokenError)
def handle_revoked_token_error(e):
    return {'message': 'Token has been revoked'}, 401


@api.errorhandler(FreshTokenRequired)
def handle_fresh_token_required(e):
    return {'message': 'Fresh token required'}, 401


@api.errorhandler(UserLoadError)
def handler_user_load_error(e):
    # The identity is already saved before this exception was raised,
    # otherwise a different exception would be raised, which is why we
    # can safely call get_jwt_identity() here
    identity = get_jwt_identity()
    return {'message': "Error loading the user {}".format(identity)}, 401


@api.errorhandler(UserClaimsVerificationError)
def handle_failed_user_claims_verification(e):
    return {'message': 'User claims verification failed'}, 401

@api.errorhandler(TypeError)
def handle_type_error(e):
    return {'message': str(e)}, 400

@api.errorhandler(500)
def handle_500_error(e):
    return {'message': str(e)}