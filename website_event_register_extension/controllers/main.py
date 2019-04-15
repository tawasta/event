# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_event_register_free.controllers.website_event \
    import WebsiteEvent
# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

class WebsiteSale(website_sale):
    
    # 1. Private attributes

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    
    # Override the method to use spesific template for free events
    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        order = request.website.sale_get_order(force_create=0)
        has_paid_tickets = bool(order.order_line)
        if request.session.get('free_tickets') and not has_paid_tickets:
            values = self.checkout_values(data={'shipping_id': -1})
            return request.website.render("website_event_register_extension.event_free_form", values)
        else:
            return super(WebsiteSale, self).checkout(**post)
