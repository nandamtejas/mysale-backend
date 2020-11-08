from database.models import *
from message_services.send_email import email

class SignUp(Resource):
    @ns_auth.expect(register)
    #@ns_auth.expect(ppsuser,validate=True)
    def post(self):
        """
        Register User
        """
        try:
            body = request.get_json()
            if body is None:
                raise BadRequest('No data is requested')
            #args = ppsuser.parse_args()
            user = User.query.filter_by(email=body['email']).all()
            email = body['email']
            if user:
                raise BadRequest(f'User with email {email} already exists')
            user = User(first_name=body['first_name'], last_name=body['last_name'], email=body['email'])#, role=body['role'])
            password = generate_password_hash(password=body['password']).decode('UTF-8')
            user.password = password
            user.created_date = datetime.now()
            db.session.add(user)
            db.session.commit()
            return {'message': 'success'}, 200
        except InternalServerError as e:
            raise BadRequest(str(e), response=400)

class LogIn(Resource):
    
    @ns_auth.expect(login)
    def post(self):
        '''
        Login
        '''
        try:
            body = request.get_json()
            if body is None:
                raise BadRequest('No data is requested')
            user = User.query.filter_by(email=body['email']).first()
            email = body['email']
            if not user:
                raise BadRequest('User with email {} not exists'.format(email))
            authorized = check_password_hash(user.password, password=body['password'])
            if not authorized:
                raise BadRequest('Incorrect Password')
            token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
            return {'message': 'success', 'token': token},200
        except InternalServerError as e:
            raise BadRequest(str(e))

class ForgotPassword(Resource):

    @ns_auth.expect(forgot)
    def post(self):
        '''
        Forgot password API
        '''
        url = request.host_url + '/reset/'
        try:
            body = request.get_json()
            if body is None:
                raise BadRequest('No data is requested')
            user_email = body['email']
            user = User.query.filter_by(email=user_email).first()
            if not user:
                raise BadRequest(f'User with email {user_email} not exists')
            token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
            email(recipients=[user_email], subject='Reset Password Request',
                    html_body=render_template('forgot.html',user=user.first_name,url=url+token),
                    text_body=render_template('forgot.txt', user=user.first_name, url=url+token))
            return {'message': "success", 'token': token},200
        except InternalServerError as e:
            raise BadRequest(e, response=400)

class ResetPassword(Resource):

    @ns_auth.expect(reset)
    def post(self, token):
        '''
        Reset password API
        '''
        try:
            body = request.get_json()
            if body is None:
                raise BadRequest('No data is requested')
            password = body['new_password']
            confirm_password = body['confirm_password']
            if password != confirm_password:
                raise BadRequest("Password didn't match")
            if token is None:
                raise BadRequest('Fields not filled')
            user_id = decode_token(token)['identity']
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise BadRequest(f"User with id {user_id} not exists")
            user.password = generate_password_hash(password)
            db.session.commit()
            from message_services.send_email import email
            return email(subject='Reset Password success',
                        recipients=[user.email],
                        html_body=render_template('reset.html', title='Reset Password Request'),
                        text_body=render_template('reset.txt', title='Reset Password Request'))
        except InternalServerError as e:
            raise BadRequest(e)


