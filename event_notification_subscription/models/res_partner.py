from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    event_interest_tags = fields.Many2many(
        "event.tag",
        string="Interested Event Tags",
        help="Select the event types you are interested in.",
    )
