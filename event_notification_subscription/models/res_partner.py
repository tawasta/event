from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    event_interest_tags = fields.Many2many(
        comodel_name="event.tag",
        string="Event Tags Interested In",
    )
