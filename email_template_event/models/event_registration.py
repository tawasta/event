# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):

    # 1. Private attributes
    _inherit = 'event.registration'

    # 2. Fields declaration
    voucher_coupons = fields.One2many(
        'wk_website.history', 'event_registration_id', compute='compute_voucher_coupons')

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def compute_voucher_coupons(self):

        for record in self:
            record.voucher_coupons = record.env['wk_website.history'].search(
                [('order_id.name', '=', record.origin), ('voucher_id.product.id', '=', record.event_ticket_id.product_id.id)])


    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
