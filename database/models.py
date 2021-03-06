from modules_and_libraries import *
from app import *
from PIL import Image

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(35), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    profile_image_url = db.Column(db.String(50), nullable=False, default='default.jpg')
    device_registration_key = db.Column(db.String(25))
    thumbnail_url = db.Column(db.String(50), default='default.jpg')
    last_online = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    categories = db.relationship('Category', backref='categories')
    vendors = db.relationship('Vendor', backref='vendors')
    deals = db.relationship('Deals', backref='deals')
    category_preference = db.relationship("UserCategoryPreference", backref='user_category_preference')
    vendor_preference = db.relationship("UserVendorPreference", backref='user_vendor_preference')
    deal_preference = db.relationship("UserDealPreference", backref='user_deal_preference')
    
    @staticmethod
    def get_all_users_to_json():
        try:
            users = User.query.order_by(User.id).all()
            output = []
            for user in users:
                user_data = {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': user.role,
                    'profile_img_url': user.profile_image_url,
                    'device_registration_key': user.device_registration_key,
                    'thumbnail_url': user.thumbnail_url,
                    'last_online': str(user.last_online),
                    'created_date': str(user.created_date),
                    'updated_date': str(user.updated_date),
                    'is_deleted': user.is_deleted,
                    'deleted_date': str(user.deleted_date)
                }
                output.append(user_data)
            return {'users': output}, 200
        except NoResultFound:
            raise BadRequest('Data Not found', response=404)
        except Exception as e:
            raise BadRequest(e, response=400)
    
    @staticmethod
    def get_user_to_json(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                raise BadRequest(f'User with id {user_id} not found')
            return {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': user.role,
                    'profile_img_url': user.profile_image_url,
                    'device_registration_key': user.device_registration_key,
                    'thumbnail_url': user.thumbnail_url,
                    'last_online': str(user.last_online),
                    'created_date': str(user.created_date),
                    'updated_date': str(user.updated_date),
                    'is_deleted': user.is_deleted,
                    'deleted_date': str(user.deleted_date)
                }
        except Exception as e:
            raise BadRequest(e, response=400)

    @staticmethod
    def save_profile_pic(profile_pic, type):
        import secrets
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(profile_pic)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
        if type == 'thumbnail':
            output_size = (10,10) 
        elif type == 'profile':
            output_size = (20,20)           
        i=Image.open(profile_pic)
        i.thumbnail(output_size)
        i.save(picture_path)
        return picture_fn


class Category(db.Model):
    __tablename__ = 'category_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order = db.Column(db.String(50))
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    vendor_category_mapping = db.relationship('VendorCategoryMapping', backref='category_vendor_mapping')
    deal_tags = db.relationship('DealTag', backref='category_deal_tags')
    user_preference = db.relationship("UserCategoryPreference", backref='user_preference')

    @staticmethod
    def get_all_categories_to_json():
        try:
            categories = Category.query.order_by(Category.id).all()
            output = []
            if not categories:
                return {'message': "Categories not found"}, 404
            for category in categories:
                output.append({
                    'id': category.id,
                    'name': category.name,
                    'image_url': category.image_url,
                    'description': category.description,
                    'order': category.order,
                    'added_by': category.added_by,
                    'created_date': str(category.created_date),
                    'updated_date': str(category.updated_date),
                    'is_deleted': category.is_deleted,
                    'deleted_date': str(category.deleted_date)
                })
            return {'categories': output}, 200
        except InternalServerError as e:
            raise BadRequest(e, response=400)
    
    @staticmethod
    def get_category_to_json(category_id):
        try:
            category = Category.query.get(category_id)
            if not category:
                return {'message': f"Category with id {category_id} not found"}, 404
            return {
                    'id': category.id,
                    'name': category.name,
                    'image_url': category.image_url,
                    'description': category.description,
                    'order': category.order,
                    'added_by': category.added_by,
                    'created_date': str(category.created_date),
                    'updated_date': str(category.updated_date),
                    'is_deleted': category.is_deleted,
                    'deleted_date': str(category.deleted_date)
                }
        except InternalServerError as e:
            raise BadRequest(e, response=400)
    
    @staticmethod
    def get_paginated_categories(page, per_page):
        try:
            categories = Category.query.paginate(page=page, per_page=per_page, error_out=False)
            if not categories:
                return {'message': "Categories not found"}, 404
            output = []
            for category in categories.items:
                output.append({
                    'id': category.id,
                    'name': category.name,
                    'image_url': category.image_url,
                    'description': category.description,
                    'order': category.order,
                    'added_by': category.added_by,
                    'created_date': str(category.created_date),
                    'updated_date': str(category.updated_date),
                    'is_deleted': category.is_deleted,
                    'deleted_date': str(category.deleted_date)
                })
            if output == []:
                return {'message': "Categories not found in page {}".format(page)}
            return {'categories': output}, 200
        except InternalServerError as e:
            return {'message': str(e)}, 400

class Vendor(db.Model):
    __tablename__ = 'vendor_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order = db.Column(db.String(50))
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    vendor_category_mapping = db.relationship('VendorCategoryMapping', backref='vendor_category_mapping')
    deals = db.relationship('Deals', backref='vendor_deals')
    user_preference = db.relationship("UserVendorPreference", backref='user_preference')

    @staticmethod
    def get_all_vendors_to_json():
        try:
            vendors = Vendor.query.order_by(Vendor.id).all()
            if not vendors:
                raise BadRequest('Vendors not found!', response=404)
            output = []
            for vendor in vendors:
                output.append({
                    'id': vendor.id,
                    'name': vendor.name,
                    'image_url': vendor.image_url,
                    'description': vendor.description,
                    'order': vendor.order,
                    'added_by': vendor.added_by,
                    'created_date': str(vendor.created_date),
                    'updated_date': str(vendor.updated_date),
                    'is_deleted': vendor.is_deleted,
                    'deleted_date': str(vendor.deleted_date)
                })
            return {'vendors': output}, 200
        except InternalServerError as e:
            return {'message': e}, 400
    
    @staticmethod
    def get_vendor_to_json(vendor_id):
        try:
            vendor = Vendor.query.get(vendor_id)
            if not vendor:
                return {'message': 'Vendor not found!'}, 404
            return {
                    'id': vendor.id,
                    'name': vendor.name,
                    'image_url': vendor.image_url,
                    'description': vendor.description,
                    'order': vendor.order,
                    'added_by': vendor.added_by,
                    'created_date': str(vendor.created_date),
                    'updated_date': str(vendor.updated_date),
                    'is_deleted': vendor.is_deleted,
                    'deleted_date': str(vendor.deleted_date)
                }, 200
        except InternalServerError as e:
            return {'message': str(e)}, 400
    
    @staticmethod
    def get_paginated_vendors(page, per_page):
        try:
            vendors = Vendor.query.paginate(page=page, per_page=per_page, error_out=False)
            if not vendors:
                return {'message', 'Vendors not found'}, 404
            output = []
            for vendor in vendors.items:
                output.append({
                    'id': vendor.id,
                    'name': vendor.name,
                    'image_url': vendor.image_url,
                    'description': vendor.description,
                    'order': vendor.order,
                    'added_by': vendor.added_by,
                    'created_date': str(vendor.created_date),
                    'updated_date': str(vendor.updated_date),
                    'is_deleted': vendor.is_deleted,
                    'deleted_date': str(vendor.deleted_date)
                })
            if output == []:
                return {'message': "Vendors not found in page {}".format(page)}, 404
            return {'vendors': output}, 200
        except InternalServerError as e:
            return {'message': str(e)}, 400


class VendorCategoryMapping(db.Model):
    __tabelname__ = 'vendor_category_mapping'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor_table.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category_table.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)

class Deals(db.Model):
    __tablename__ = 'deals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(50), nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor_table.id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    is_available = db.Column(db.Boolean, default=False)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    deal_tags = db.relationship('DealTagMapping', backref='deal_tags')
    user_preference = db.relationship("UserDealPreference", backref='user_preference')

    @staticmethod
    def get_all_deals_to_json():
        try:
            deals = Deals.query.order_by(Deals.id).all()
            output = []
            for deal in deals:
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
            return {'deals': output}, 200
        except InternalServerError:
            return {'message': str(e)}, 400
    
    @staticmethod
    def get_deal_to_json(deal_id):
        try:
            deal = Deals.query.get(deal_id)
            if not deal:
                return {'message': 'Deal not found'}, 404
            return {
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
            }, 200
        except InternalServerError as e:
            return {'message': str(e)}, 400
    
    @staticmethod
    def get_paginated_deals(page, per_page):
        try:
            deals = Deals.query.paginate(page=page, per_page=per_page, error_out=False)
            if not deals:
                return {'message': 'Deals not found!!'}, 404
            output = []
            for deal in deals.items:
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
            if output == []:
                return {'message': "Deals not found in page {}".format(page)}, 404
            return {'deals': output}, 200
        except InternalServerError as e:
            return {'message': str(e)}, 400

class DealTag(db.Model):
    __tablename__ = 'deal_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35))
    category_id = db.Column(db.Integer, db.ForeignKey('category_table.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    deal_tag_mapping = db.relationship('DealTagMapping', backref='tag_mapping')


class DealTagMapping(db.Model):
    __tablename__ = 'deal_tag_mapping'
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('deal_tag.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)

class UserCategoryPreference(db.Model):
    __tablename__ = 'category_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category_table.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)


class UserVendorPreference(db.Model):
    __tablename__ = 'vendor_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor_table.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)

class UserDealPreference(db.Model):
    __tablename__ = 'deal_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)

db.create_all()