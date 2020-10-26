from database.models import *

class CreateDeals(Resource):

    @jwt_required
    @ns_deals.expect(deals)
    def post(self):
        """
        Create deals
        Caution: Only admins can create
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to create the deals"}, 400
            body = request.get_json()
            if body is None:
                raise SchemaValidationError
            if not Vendor.query.get(body['vendor_id']):
                return {'message': "Vendor not found!!"}, 404
            deals = Deals(name=body['name'], image_url=body['image_url'])
            deals.start_date = datetime.strptime(body['start_date'], r'%d-%m-%Y %I:%M %p')
            deals.end_date = datetime.strptime(body['end_date'], r'%d-%m-%Y %I:%M %p')
            deals.added_by = user_id
            deals.vendor_id = body['vendor_id']
            deals.created_date = datetime.now()
            db.session.add(deals)
            db.session.commit()
            return {'message': 'Success'}, 200
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'], response=400)
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except InternalServerError:
            handle_error_internal_server(errors)

    @jwt_required
    @ns_deals.expect(pagination, validate=True)
    def get(self):
        """
        retrieve all deals
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            args = pagination.parse_args()
            page = args.get('page',1)
            per_page = args.get('per_page', 10)
            return Deals.get_paginated_deals(page=page, per_page=per_page)
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)

class UpdateDeals(Resource):

    @jwt_required
    def get(self, id):
        """
        retrieve the deal
        id: deal id
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            return Deals.get_deal_to_json(deal_id=id)
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)

    @jwt_required
    def delete(self, id):
        """
        delete the deal
        id: deal id
        Caution: Only admin can delete deal
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                raise BadRequest("No rights to delete deals", response=400)
            deal = Deals.query.get(id)
            if not deal:
                raise BadRequest('Deal not found!!', response=404)
            db.session.delete(deal)
            db.session.commit() 
            return {'message': 'Success'}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except InternalServerError:
            return {'message': str(e)}, 400
    
    @jwt_required
    @ns_deals.expect(deals)
    def put(self, id):
        """
        Update the deal
        id: deal id
        Caution: Only admin can update the deal
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                raise BadRequest('No rights to update deals')
            body = request.get_json()
            if body is None or not body:
                raise SchemaValidationError
            if not Vendor.query.get(body['vendor_id']):
                return {'message': "Vendor not found!!"}, 404
            deal = Deals.query.get(id)
            deal.name = body['name']
            deal.image_url = body['image_url']
            deal.start_date = datetime.strptime(body['start_date'], r"%d-%m-%Y %I:%M %p")
            deal.end_date = datetime.strptime(body['end_date'], r"%d-%m-%Y %I:%M %p")
            deal.vendor_id = body['vendor_id']
            deal.updated_date = datetime.now()
            db.session.commit()
            return {'message': 'Success'}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists",response=404)
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'], response=400)

class GetDealsinDate(Resource):

    @jwt_required
    def get(self, days_ahead=7):
        """
        retrieve deals for 7 days before from start date of deal
        days_ahead: total days from now to start date of deals
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            deals = Deals.query.order_by(Deals.id).all()
            if not deals:
                return {'message': "Deals not found!!"}, 404
            output = []
            for deal in deals:
                rem_days = deal.start_date - datetime.now()
                if 0 <= rem_days.days <= int(days_ahead):
                    output.append({
                    'id': deal.id,
                    'name': deal.name,
                    'image_url': deal.image_url,
                    'vendor_id': deal.vendor_id,
                    'start_date': str(deal.start_date),
                    'end_date': str(deal.end_date),
                    'added_by': deal.added_by,
                    'created_date': str(deal.created_date),
                    'updated_date': str(deal.updated_date),
                    'is_deleted': str(deal.is_deleted),
                    'deleted_date': str(deal.deleted_date)
                    })
            return {'upcomming_deals': output}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except InternalServerError:
            return {'message': str(e)}, 400
        
class CreateDealTags(Resource):

    @jwt_required
    @ns_deals.expect(deal_tags)
    def post(self):
        """
        Create Deal Tags
        Caution: Only admins can view
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                raise BadRequest("No rights to create deal tags")
            body = request.get_json()
            if not body or body is None:
                raise SchemaValidationError
            if not Category.query.get(body['category_id']):
                return {'message': "Category not found!!"}, 404
            tag = DealTag(name=body['name'])
            tag.category_id = body['category_id']
            tag.created_date = datetime.now()
            db.session.add(tag)
            db.session.commit()
            return {'message': "Success"}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'], response=404)
    
    @jwt_required
    def get(self):
        """
        Get deal tags
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            deal_tags = DealTag.query.order_by(DealTag.id).all()
            if not deal_tags:
                return {'message': 'Deal tags not found!!'}, 404
            output = []
            for deal in deal_tags:
                output.append({
                    'id': deal.id,
                    'name': deal.name,
                    'category_id': deal.category_id,
                    'created_date': str(deal.created_date),
                    'updated_date': str(deal.updated_date),
                    'is_deleted': deal.is_deleted,
                    'deleted_date': str(deal.deleted_date)
                })
            return {'deal_tags': output}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)

