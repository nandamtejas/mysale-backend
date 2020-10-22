from database.models import *

class GetUsers(Resource):

    @jwt_required
    def get(self):
        '''
        get all users
        '''
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            return User.get_all_users_to_json()
        except InternalServerError as e:
            raise BadRequest(e, response=400)
        except UserNotExistsError:
            raise BadRequest(errors['UserNotExistsError']['message'], response=404)
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401

class UpdateUsers(Resource):

    @jwt_required
    def get(self,id):
        '''
        get one user
        id: id of the user to fetch their details
        return: returns the details of user_id
        '''
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                raise BadRequest("User has no rights to view others accounts")
            return User.get_user_to_json(id)
        except UserNotExistsError:
            raise BadRequest(errors['UserNotExistsError']['message'], response=404)
        except InternalServerError as e:
            raise BadRequest(e, response=400)
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401

    @jwt_required
    @ns_users.expect(update_user)
    def put(self, id):
        '''
        update the user 
        id: id of the user to be updated
        return: update the account of id

        Caution: only admins can update user
        '''
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                raise BadRequest('User has no rights to update other accounts')
            body = request.get_json()
            if body is None:
                raise SchemaValidationError
            to_update = User.query.get(id)
            if not to_update:
                raise UserNotExistsError
            if User.query.filter_by(email=body['email']).all():
                raise UserAlreadyExistsError
            to_update.first_name = body['first_name']
            to_update.last_name = body['last_name']
            to_update.email = body['email']
            to_update.role = body['role']
            to_update.updated_date = datetime.now()
            db.session.commit()
            return {'message': 'success'}, 200
        except UserNotExistsError:
            raise BadRequest(f'User with id {id} not exists', response=404)
        except UserAlreadyExistsError:
            raise BadRequest(errors['UserAlreadyExistsError']['message'], response=402)
        except InternalServerError as e:
            raise BadRequest(e, response=400)
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401
    
    @jwt_required
    def delete(self, id):
        '''
        deletes the user
        id: id of the user to be deleted
        return: returns success when deleted

        Caution: only admins can delete user
        '''
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                raise BadRequest('User has no rights to delete',response=400)
            to_delete = User.query.get(id)
            if not to_delete:
                raise BadRequest(f'User with id {id} not exists',response=404)
            db.session.delete(to_delete)
            db.session.commit()
            return {'message': 'success'}, 200
        except UserNotExistsError:
            raise BadRequest(errors['UserNotExistsError']['message'], response=404)
        except InternalServerError as e:
            raise BadRequest(e, response=400)
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401


