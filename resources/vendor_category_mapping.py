from database.models import *

class VendorCategoryMappingAPI(Resource):

    @jwt_required
    @ns_ven_cat_map.expect(vendor_category_mapping)
    def post(self):
        """
        create vendor category mapping
        Caution: Only admins can create vendor category mapping
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to create vendor category preferences"}, 400
            body = request.get_json()
            if not body or body is None:
                raise SchemaValidationError
            vcms = body['vendor_category_mapping']
            output = []
            for vcm in vcms:
                c_id, v_id = vcm['category_id'], vcm['vendor_id']
                if not Category.query.get(c_id):
                    return {'message': "Category with id {} not found".format(c_id)}, 404
                if not Vendor.query.get(v_id):
                    return {'message': "Vendor with id {} not found".format(v_id)}, 404
                ggs = VendorCategoryMapping(category_id=c_id, vendor_id=v_id)
                ggs.created_date = datetime.now()
                output.append(ggs)
            db.session.add_all(output)
            db.session.commit()
            return {'message': "Success"},200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'])
    
    @jwt_required
    @ns_ven_cat_map.expect(pagination, validate=True)
    def get(self):
        """
        get all vendor category mapping
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            args = pagination.parse_args()
            page = args.get('page', 1)
            per_page = args.get('per_page', 10)
            vcms = VendorCategoryMapping.query.paginate(page=page, per_page=per_page, error_out=False)
            if not vcms:
                return {'message': "vendor category mapping not found"}, 404
            output = []
            for vcm in vcms.items:
                output.append({
                    'id': vcm.id,
                    'vendor_id': vcm.vendor_id,
                    'category_id': vcm.category_id,
                    'created_date': str(vcm.created_date),
                    'updated_date': str(vcm.updated_date),
                    'is_deleted': vcm.is_deleted,
                    'deleted_date': str(vcm.deleted_date)
                })
            if output == []:
                return {'message': "vendor category mappings not found in page {}".format(page)}, 404
            return {'vendor_category_mapping': output}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=400)


class UpdateVendorCategoryMappingAPI(Resource):

    @jwt_required
    def delete(self, id):
        """
        delete vendor category mapping
        Caution: Only admins can delete
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to delete"}, 400
            vcm = VendorCategoryMapping.query.get(id)
            if not vcm:
                return {'message': "vendor category mapping not found!!"}, 404
            db.session.delete(vcm)
            db.session.commit()
            return {'message': "Success"}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists")
    
    @jwt_required
    def get(self,id):
        """
        get vendor category mapping
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            vcm = VendorCategoryMapping.query.get(id)
            if not vcm:
                return {'message': "vendor category mapping not found!!"}, 404
            return {
                'id': vcm.id,
                'vendor_id': vcm.vendor_id,
                'category_id': vcm.category_id,
                'created_date': str(vcm.created_date),
                'updated_date': str(vcm.updated_date),
                'is_deleted': vcm.is_deleted,
                'deleted_date': str(vcm.deleted_date)
            }, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists")

    @jwt_required
    @ns_ven_cat_map.expect(ven_cat)
    def put(self, id):
        """
        update vendor category mapping
        Caution: Only admins can update
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to delete"}, 400
            vcm = VendorCategoryMapping.query.get(id)
            if not vcm:
                return {'message': "vendor category mapping not found!!"}, 404
            body = request.get_json()
            if not body or body is None:
                raise SchemaValidationError
            c_id, v_id = body['category_id'], body['vendor_id']
            if not Category.query.get(c_id):
                return {'message': "Category with id {} not found".format(c_id)}, 404
            if not Vendor.query.get(v_id):
                return {'message': "Vendor with id {} not found".format(v_id)}, 404
            vcm.vendor_id = v_id
            vcm.category_id = c_id
            vcm.updated_date = datetime.now()
            db.session.commit()
            return {'message': "Success"}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'])