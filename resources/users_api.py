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


class UserCatMapAPI(Resource):

    @jwt_required
    @ns_user_cat_map.expect(user_category_preferences)
    def post(self):
        """
        create User Category Preference
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            body = request.get_json()
            if not body:
                raise SchemaValidationError
            ucps = body['user_category_preferences']
            for ucp in ucps:
                if ucp['is_deleted'] == True:
                    ggs = UserCategoryPreference.query.filter_by(user_id=user_id, category_id=ucp['category_id']).first()
                    if not ggs:
                        continue
                    ggs.is_deleted = True
                    ggs.deleted_date = datetime.now()
                    db.session.commit()
                else:
                    if UserCategoryPreference.query.filter_by(user_id=user_id, category_id=ucp['category_id']).first():
                        continue
                    ggs = UserCategoryPreference(user_id=user_id, category_id=ucp['category_id'])
                    ggs.created_date = datetime.now()
                    db.session.add(ggs)
                    db.session.commit()
            return {'message': 'Success'}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'], response=404)
    
    @jwt_required
    @ns_user_cat_map.expect(pagination, validate=True)
    def get(self):
        """
        Get all user category preferences
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            args = pagination.parse_args()
            page = args.get('page', 1)
            per_page = args.get('per_page', 10)
            ucps = UserCategoryPreference.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
            if not ucps:
                return {'message': 'User Category Preferences not found'}, 404
            output = []
            for ucp in ucps.items:
                output.append({
                    'id': ucp.id,
                    'user_id': ucp.user_id,
                    'category_id': ucp.category_id,
                    'created_date': str(ucp.created_date),
                    'updated_date': str(ucp.updated_date),
                    'is_deleted': ucp.is_deleted,
                    'deleted_date': str(ucp.deleted_date)
                })
            if output == []:
                return {'message': 'User Category Preferences not found in page {}'.format(page)}, 404
            return {'user_category_preferences': output}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except InternalServerError as e:
            return {'message': str(e)}, 400
