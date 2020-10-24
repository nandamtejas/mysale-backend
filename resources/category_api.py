from database.models import * 

class CatagoriesCreate(Resource):

    @jwt_required
    def get(self):
        '''
        get all the categories
        '''
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            return Category.get_all_categories_to_json()
        except InternalServerError as e:
            raise BadRequest(errors['InternalServerError']['message'])
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exist")
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401
    
    @jwt_required
    @ns_category.expect(category)
    def post(self):
        '''
        create the category
        
        Caution: Only admins can create category
        '''
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to create the category"}, 400
            body = request.get_json()
            category = Category(name=body['name'], image_url=body['image_url'],description=body['description'],order=body['order'])
            db.session.add(category)
            category.added_by = user_id
            category.created_date = datetime.now()
            db.session.commit()
            return {'message': 'success'}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except InternalServerError as e:
            raise BadRequest(e, response=400)
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401

class UpdateCategory(Resource):

    @jwt_required
    def get(self,id):
        """
        Get the category 
        id: category id
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            return Category.get_category_to_json(category_id=id)
        except InternalServerError as e:
            return {'message': e}, 400
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exist", response=404)
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401
    
    @jwt_required
    def delete(self, id):
        """
        Delete the category
        id: category id
        Caution: Only admins can delete the category
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to delete the category"}, 400
            category = Category.query.get(id)
            if not category:
                return {'message': "Category not found"}, 404
            db.session.delete(category)
            db.session.commit()
            return {'message': "Success"}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists")
        except InternalServerError as e:
            return {'message': e}, 400
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401
    
    @jwt_required
    @ns_category.expect(category)
    def put(self, id):
        """
        Update the category

        id: category id
        Caution: Only admins can update
        """
        try: 
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': 'No rights to update the category'}, 400
            body = request.get_json()
            if body is None:
                raise SchemaValidationError
            category = Category.query.get(id)
            if not category:
                return {'message': 'Category not found'}, 404
            category.name = body['name']
            category.image_url = body['image_url']
            category.description = body['description']
            category.order = body['order']
            category.updated_date = datetime.now()
            db.session.commit()
            return {'message': 'Success'}, 200
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'])
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists")
        except InternalServerError as e:
            return {'message': e}, 400
        except NoAuthorizationError:
            return {'message': 'Authorization header missing'}, 401
    