# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import http
from openerp.http import request
from openerp.addons.website_event_sale.controllers.main import website_event
# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

class WebsiteEvent(website_event):
    
    # 1. Private attributes

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    
    # Change redirect to go cart instead of checkout form 
    @http.route(['/event/cart/update'], type='http', auth="public",
                methods=['POST'], website=True)
    def cart_update(self, **post):
        super(WebsiteEvent, self).cart_update(**post)
        return request.redirect("/shop/cart")
