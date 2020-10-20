from app import *
from resources.auth import *
from resources.users_api import *
from resources.category_api import *
from resources.vendor_api import *

ns_auth.add_resource(SignUp, '/register')
ns_auth.add_resource(LogIn, '/login')
ns_auth.add_resource(ForgotPassword, '/forgot')
ns_auth.add_resource(ResetPassword, '/reset/<token>')
ns_users.add_resource(GetUsers, '/all_users')
ns_users.add_resource(UpdateUsers, '/user/<int:id>')
ns_category.add_resource(CatagoriesCreate, '/')
ns_category.add_resource(UpdateCategory, '/<int:id>')
ns_vendor.add_resource(VendorCreate, '/')
ns_vendor.add_resource(UpdateVendor, '/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)