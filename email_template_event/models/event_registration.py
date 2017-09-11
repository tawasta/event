# -*- coding: utf-8 -*-

# 1. Standard library imports:
import vobject

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

    qr_string = fields.Char(string="User's vCard for QR", compute='compute_qr_string')
    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def compute_voucher_coupons(self):

        for record in self:
            record.voucher_coupons = record.env['wk_website.history'].search(
                [('order_id.name', '=', record.origin), ('voucher_id.product.id', '=', record.event_ticket_id.product_id.id)])

    @api.multi
    def compute_qr_string(self):

        for record in self:

            name = record.name
            organisation = record.partner_id.company_name or ''
            title = ''
            if record.organization_role:
                title = dict(record.fields_get(
                    ['organization_role'])['organization_role']['selection'])[record.organization_role]
            email = record.email or ''
            
            record.qr_string = "BEGIN:VCARD;N:%s;TITLE:%s;ORG:%s;EMAIL:%s;END:VCARD" % (name, title, organisation, email)

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
