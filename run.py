from app import *
from resources.auth import *
from resources.users_api import *
from resources.category_api import *
from resources.vendor_api import *
from resources.deals_api import *
from resources.vendor_category_mapping import *

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
ns_deals.add_resource(CreateDeals, '/')
ns_deals.add_resource(UpdateDeals, '/<int:id>')
ns_deals.add_resource(GetDealsinDate, '/deals_ahead/<int:days_ahead>')
ns_deals.add_resource(CreateDealTags, '/deal_tags')
ns_deals.add_resource(UpdateDealTags, '/deal_tag/<int:id>')
ns_user_cat_map.add_resource(UserCatMapAPI, '/categories')
ns_user_cat_map.add_resource(UpdateUserCatMap, '/category/<int:id>')
ns_user_vend_map.add_resource(UserVenMapAPI, '/vendors')
ns_user_vend_map.add_resource(UpdateUserVenMap, '/vendor/<int:id>')
ns_user_deals_map.add_resource(UserDealMap, '/deals')
ns_user_deals_map.add_resource(UpdateUserDealPreference, '/deal/<int:id>')
ns_deal_tag_map.add_resource(MappingDealsAndTags, '/')
ns_deal_tag_map.add_resource(UpdateDealTagMapping, '/<int:id>')
ns_ven_cat_map.add_resource(VendorCategoryMappingAPI, '/')
ns_ven_cat_map.add_resource(UpdateVendorCategoryMappingAPI, '<int:id>')

if __name__ == '__main__':
    app.run(debug=True)