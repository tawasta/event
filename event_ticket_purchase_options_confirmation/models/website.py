from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    event_invitation_confirmation_help = fields.Html(
        string="Registration Instructions on Order Confirmation",
        translate=True,
    )
