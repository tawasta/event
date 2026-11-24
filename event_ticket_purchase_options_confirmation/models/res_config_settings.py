from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    event_invitation_confirmation_help = fields.Html(
        related="website_id.event_invitation_confirmation_help",
        readonly=False,
    )
