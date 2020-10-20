from database.models import *

class VendorCreate(Resource):

    @jwt_required
    def get(self):
        """
        get all vendors
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            return Vendor.get_all_vendors_to_json()
        except UserNotExistsError:
            raise BadRequest('User with id {} not found'.format(user_id),response=404)
        except InternalServerError as e:
            return {'message': e}, 400
    
    @jwt_required
    @ns_vendor.expect(vendor)
    def post(self):
        """
        Create Vendors
        Caution: Only admins can create vendors
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to create vendor"}, 400
            body = request.get_json()
            if not body:
                raise SchemaValidationError
            vendor = Vendor(name=body['name'], image_url=body['image_url'], description=body['description'], order=body['order'])
            db.session.add(vendor)
            vendor.added_by = user_id
            db.session.commit()
            return {'message': 'Success'}, 200
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'], response=404)
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except InternalServerError as e:
            return {'message': e}, 400


class UpdateVendor(Resource):

    @jwt_required
    def get(self, id):
        """
        retrieve the vendor
        id: vendor id
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            return Vendor.get_vendor_to_json(vendor_id=id)
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except InternalServerError as e:
            return {'message': e}, 400
    
    @jwt_required
    def delete(self,id):
        """
        Delete the vendor
        id: vendor id
        Caution: Only admins can delete
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to create vendor"}, 400
            vendor = Vendor.query.get(id)
            if not vendor:
                return {'message': 'Vendor not found!'}, 404
            db.session.delete(vendor)
            db.session.commit()
            return {'message': 'Success'}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id{user_id} not exists")
        except InternalServerError as e:
            return {'message': e}, 400
    
    @jwt_required
    @ns_vendor.expect(vendor)
    def put(self, id):
        """
        update the vendor
        id: vendor id
        Caution: Only admins can update the vendor
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to create vendor"}, 400
            vendor = Vendor.query.get(id)
            if not vendor:
                return {'message': 'Vendor not found!'}, 404
            body = request.get_json()
            if not body:
                raise SchemaValidationError
            vendor.name = body['name']
            vendor.image_url = body['image_url']
            vendor.description = body['description']
            vendor.order = body['order']
            db.session.commit()
            return {'message': 'Success'}, 200
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'], response=400)
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except InternalServerError as e:
            return {'message': e}, 400
