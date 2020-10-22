from database.models import *

class CreateDeals(Resource):

    @jwt_required
    @ns_deals.expect(deals)
    def post(self, vendor_id):
        return ''