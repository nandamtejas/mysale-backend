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
    @ns_deals.expect(pagination, validate=True)
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
            args = pagination.parse_args()
            page = args.get('page', 1)
            per_page = args.get('per_page', 10)
            deals = Deals.query.order_by(Deals.id).paginate(page=page, per_page=per_page, error_out=False)
            if not deals:
                return {'message': "Deals not found!!"}, 404
            output1 = []
            # check upcomming deals within days_ahead
            for deal in deals.items:
                rem_days = deal.start_date - datetime.now()
                if 0 <= rem_days.days <= int(days_ahead):
                    output1.append({
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
            # if deals not found within days ahead the retrieve all upcomming deals within start date
            if output1 == []:
                for deal in deals.items:
                    if datetime.now() <= deal.start_date:
                        output1.append({
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
            output = output1
            if output == []:
                return {'message': "deals not found in page {}".format(page)}, 404
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
    @ns_deals.expect(pagination, validate=True)
    def get(self):
        """
        Get deal tags
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            args = pagination.parse_args()
            page = args.get('page', 1)
            per_page = args.get('per_page', 10)
            deal_tags = DealTag.query.order_by(DealTag.id).paginate(page=page, per_page=per_page, error_out=False)
            if not deal_tags:
                return {'message': 'Deal tags not found!!'}, 404
            output = []
            for deal in deal_tags.items:
                output.append({
                    'id': deal.id,
                    'name': deal.name,
                    'category_id': deal.category_id,
                    'created_date': str(deal.created_date),
                    'updated_date': str(deal.updated_date),
                    'is_deleted': deal.is_deleted,
                    'deleted_date': str(deal.deleted_date)
                })
            if output == []:
                return {'message': "Deal tags not found in page {}".format(page)}, 404
            return {'deal_tags': output}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)

class UpdateDealTags(Resource):

    @jwt_required
    def delete(self, id):
        """
        delete deal tag
        id: deal tag id
        Caution: Only admins can delete
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to delete deal tags"}, 400
            tag = DealTag.query.get(id)
            if not tag:
                return {'message': "Deal tag not found!"}, 404
            db.session.delete(tag)
            db.session.commit()
            return {'message': "Success"}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)

    @jwt_required
    def get(self, id):
        """
        get the deal tag
        id: deal tag id
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            deal = DealTag.query.get(id)
            return {
                'id': deal.id,
                'name': deal.name,
                'category_id': deal.category_id,
                'created_date': str(deal.created_date),
                'updated_date': str(deal.updated_date),
                'is_deleted': deal.is_deleted,
                'deleted_date': str(deal.deleted_date)
            }, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
    
    @jwt_required
    @ns_deals.expect(deal_tags)
    def put(self, id):
        """
        update deal tag
        id: deal tag id
        Caution: Only admins can update deal tag
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No access to update deal tag"}, 400
            tag = DealTag.query.get(id)
            if not tag:
                return {'message':"Deal tag with id {} not found".format(id)}, 404
            body = request.get_json()
            if not body:
                raise SchemaValidationError
            tag.name = body['name']
            tag.category_id = body['category_id']
            tag.updated_date = datetime.now()
            db.session.commit()
            return {'message':"Success"}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'], response=404)
 

class MappingDealsAndTags(Resource):

    @jwt_required
    @ns_deal_tag_map.expect(deal_tag_mapping)
    def post(self):
        """
        create deal tag mapping
        Caution: Only admins create deal tag mapping
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': 'No access to create deal tag mapping'}, 400
            body = request.get_json()
            if not body or body is None:
                raise SchemaValidationError
            dtms = body['deal_tag_mapping']
            if dtms is None:
                raise SchemaValidationError
            output = []
            for dtm in dtms:
                d_id, t_id = dtm['deal_id'], dtm['tag_id']
                if not Deals.query.get(d_id):
                    return {'message': 'Deal with id {} not found'.format(d_id)}, 404
                if not DealTag.query.get(t_id):
                    return {'message': 'Deal Tag with id {} not found'.format(t_id)}, 404
                d = DealTagMapping(deal_id=d_id, tag_id=t_id)
                d.created_date = datetime.now()
                output.append(d)
            db.session.add_all(output)
            db.session.commit()
            return {'message': "Success"}, 200
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'],response=400)
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
    
    @jwt_required
    @ns_deal_tag_map.expect(pagination,validate=True)
    def get(self):
        """
        get all deal tag mapping
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            args = pagination.parse_args()
            page = args.get('page', 1)
            per_page = args.get('per_page',10)
            dtms = DealTagMapping.query.paginate(page=page, per_page=per_page, error_out=False)
            output = []
            for dtm in dtms.items:
                output.append({
                    'id': dtm.id,
                    'deal_id': dtm.deal_id,
                    'tag_id': dtm.tag_id,
                    'created_date': str(dtm.created_date),
                    'updated_date': str(dtm.updated_date),
                    'is_deleted': dtm.is_deleted,
                    'deleted_date': str(dtm.deleted_date)
                })
            if output == []:
                return {'message': "Deal tag Mappings not found in page {}".format(page)}, 404
            return {'deal_tag_mapping': output}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'], response=400)

class UpdateDealTagMapping(Resource):

    @jwt_required
    def delete(self, id):
        """
        delete deal tag mapping
        Caution: Only admins can delete
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to delete deal tag mapping"}, 400
            dtm = DealTagMapping.query.get(id)
            if not dtm:
                return {'message': "Deal tag mapping not found"}, 404
            db.session.delete(dtm)
            db.session.commit()
        except UserNotExists:
            raise BadRequest(f"User with id {user_id} not exists", response=404)

    @jwt_required
    def get(self, id):
        """
        get deal tag mapping
        id: deal tag mapping id
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            dtm = DealTagMapping.query.get(id)
            if not dtm:
                return {'message': "Deal tag mapping not found"}, 404
            return {
                'id': dtm.id,
                'deal_id': dtm.deal_id,
                'tag_id': dtm.tag_id,
                'created_date': str(dtm.created_date),
                'updated_date': str(dtm.updated_date),
                'is_deleted': dtm.is_deleted,
                'deleted_date': str(dtm.deleted_date)
            }, 200
        except UserNotExistsError:
            raise Badrequest(f"User with id {user_id} not exists", response=404)

    @jwt_required
    @ns_deal_tag_map.expect(deal_tag_map)
    def put(self, id):
        """
        update deal tag mapping
        id: deal tag mapping id
        Caution: Only admin can update
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            if user.role != 'admin':
                return {'message': "No rights to delete deal tag mapping"}, 400
            body = request.get_json()
            if not body or body is None:
                raise SchemaValidationError
            dtm = DealTagMapping.query.get(id)
            if not dtm:
                return {'message': "Deal tag mapping not found"}, 404
            d_id, t_id = body['deal_id'], body['tag_id']
            if not Deals.query.get(d_id):
                return {'message': 'Deal with id {} not found'.format(d_id)}, 404
            if not DealTag.query.get(t_id):
                return {'message': 'Deal Tag with id {} not found'.format(t_id)}, 404
            dtm.deal_id = d_id
            dtm.tag_id = t_id
            dtm.updated_date = datetime.now()
            db.session.commit()
            return {'message': "Success"}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists", response=404)
        except SchemaValidationError:
            raise BadRequest(errors['SchemaValidationError']['message'])
