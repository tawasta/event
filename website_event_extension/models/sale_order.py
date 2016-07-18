# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import api, fields, models, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class SaleOrder(models.Model):

    # 1. Private attributes
    _inherit = 'sale.order'

    # 2. Fields declaration
    new_header = fields.Char(
        string=_('Invoice header'),
        compute='compute_new_header'
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def compute_new_header(self):

        header = ""
        for record in self:
            for line in record.order_line:
                event_name = line.event_id.name_get()
                if 0 in event_name and 1 in event_name[0]:
                    header_msg = event_name[0][1]
                else:
                    header_msg = ""

                header += _(header_msg) or ""

                header += ("\n " +
                           line.event_ticket_id.name) if line.event_ticket_id.name else ""
            record.new_header = header
            header = ""

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    @api.model
    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        # DO NOT REMOVE THIS METHOD
        # While it seems to do nothing, it will actually set the context for the method
        #
        # We need to add "if not context: context = {}" to this function in website_event_sale,
        # so it will work even when the method is called without context.
        # The decorator will do it automatically, so we don't need to add anything manually.

        return super(SaleOrder, self)._cart_find_product_line(product_id=product_id, line_id=line_id, **kwargs)
