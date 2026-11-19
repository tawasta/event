from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    event_registration_self_help = fields.Html(
        related="website_id.event_registration_self_help",
        readonly=False,
    )
    event_registration_others_help = fields.Html(
        related="website_id.event_registration_others_help",
        readonly=False,
    )
