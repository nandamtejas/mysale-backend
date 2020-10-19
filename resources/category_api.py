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
            raise BadRequest(errors['InternalServerError']['message'], response=400)
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exist")
    
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
                raise BadRequest('No access to create the category', response=400)
            body = request.get_json()
            category = Category(name=body['name'], image_url=body['image_url'],description=body['description'],order=body['order'])
            db.session.add(category)
            category.added_by = user_id
            db.session.commit()
            return {'message': 'success'}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except InternalServerError as e:
            raise BadRequest(e, response=400)

