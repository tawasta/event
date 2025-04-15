from odoo import models, fields, http, _
from odoo.http import request
from odoo.tools.safe_eval import safe_eval

class EventEventTicket(models.Model):
    _inherit = 'event.event.ticket'

    paywall_domain = fields.Char(
        string="Paywall Domain",
        help="Comma-separated domains for which this ticket is visible."
    )

    user_in_paywall_domain = fields.Boolean(
        string="User has access to paywall content",
        compute="_compute_user_in_paywall_domain",
    )

    def _compute_user_in_paywall_domain(self):
        partner = self.env["res.partner"].sudo()
        partner_id = self.env.user.partner_id.id

        for record in self:
            paywall_domain = False
            if record.paywall_domain:
                paywall_domain = [("id", "=", partner_id)] + safe_eval(
                    record.paywall_domain
                )

            if paywall_domain and partner.search(paywall_domain):
                record.user_in_paywall_domain = True
            else:
                record.user_in_paywall_domain = False