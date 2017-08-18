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
            if not record.origin:
                continue

            invoice = record.env['account.invoice'].search([
                ('name', '=', record.origin),
                ('company_id', '=', record.company_id.id),
            ], limit=1)

            # The origin is a SO-name
            if not invoice:
                sale_order = self.env['sale.order'].search([
                    ('name', '=', record.origin),
                    ('company_id', '=', record.company_id.id),
                ], limit=1)

                # TODO: what if multiple invoices?
                if sale_order.invoice_ids:
                    invoice = sale_order.invoice_ids[0]

            if invoice:
                record.invoice = invoice.id
                record.invoice_state = invoice.state

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
