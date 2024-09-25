from odoo import fields, models


class EventTicket(models.Model):
    _inherit = "event.event.ticket"

    required_subscription_id = fields.Many2one(
        string="Required subscription",
        help="This subscription is required for buying this ticket",
    )
