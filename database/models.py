#from modules_and_libraries import *
from app import *
from PIL import Image

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(35), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    profile_image_url = db.Column(db.String(50), nullable=False, default='default.jpg')
    device_registration_key = db.Column(db.String(100))
    thumbnail_url = db.Column(db.String(50), default='default.jpg')
    last_online = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    categories = db.relationship('Category', backref='categories')
    vendors = db.relationship('Vendor', backref='vendors')
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
            return output
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
            if not categories:
                raise NoResultFound
            output = []
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
            return output
        except NoResultFound:
            raise BadRequest('Categories Not found', response=404)
        except InternalServerError as e:
            raise BadRequest(e, response=400)
    
    @staticmethod
    def get_category_to_json(category_id):
        try:
            category = Category.query.get(category_id)
            if not category:
                raise BadRequest('Category Not Found', response=404)
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
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    deal_tags = db.relationship('DealTagMapping', backref='deal_tags')
    user_preference = db.relationship("UserDealPreference", backref='user_preference')

class DealTag(db.Model):
    __tablename__ = 'deal_tag'
    id = db.Column(db.Integer, primary_key=True)
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