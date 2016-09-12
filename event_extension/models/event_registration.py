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
    invoice = fields.Many2one('account.invoice', "Invoice", compute='compute_account_invoice')
    invoice_state = fields.Char('Invoice state', compute='compute_account_invoice')

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def compute_account_invoice(self):
        for record in self:
            invoice = self.env['account.invoice'].search([
                ('name', '=', record.origin),
                ('company_id', '=', record.company_id.id),
            ], limit=1)

            if invoice:
                record.invoice = invoice.id
                record.invoice_state = invoice.state

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
