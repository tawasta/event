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
    qr_string = fields.Char(string="User's vCard for QR", compute='compute_qr_string')
    qr_string_stored = fields.Char(string="User's vCard for QR", compute='compute_qr_string', store=True, copy=False)

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    @api.depends('name', 'email', 'partner_id', 'partner_id.parent_id.name', 'partner_id.function')
    def compute_qr_string(self):
        
        for record in self:

            name = record.name
            organisation = record.partner_id.company_name
            title = record.partner_id.function
            email = record.email
            
            record.qr_string = "BEGIN:VCARD;N:%s;TITLE:%s;ORG:%s;EMAIL:%s;END:VCARD" % (name, title, organisation, email)

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
