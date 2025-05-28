from odoo import models, fields, http, _
from odoo.http import request
from odoo.tools.safe_eval import safe_eval


class EventEventTicket(models.Model):
    _inherit = "event.event.ticket"

    partner_domain_filter_ids = fields.Many2many(
        "partner.domain.filter",
        string="Partner filters",
    )

    user_in_partner_domain = fields.Boolean(
        string="User has access to this product",
        compute="_compute_user_in_partner_domain",
    )

    def _compute_user_in_partner_domain(self):
        partner = self.env["res.partner"].sudo()
        user_partner_id = self.env.user.partner_id.id
        for record in self:
            user_in_partner_domain = False
            for partner_domain in record.partner_domain_filter_ids:
                domain = [("id", "=", user_partner_id)] + safe_eval(
                    partner_domain.filter_domain
                )
                if partner.search(domain):
                    user_in_partner_domain = True

            record.user_in_partner_domain = (
                user_in_partner_domain or not record.partner_domain_filter_ids
            )
