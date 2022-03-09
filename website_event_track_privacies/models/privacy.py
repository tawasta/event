from odoo import models, fields


class PrivacyActivity(models.Model):
    _inherit = "privacy.activity"

    show_in_event = fields.Boolean(
        default=False,
        string="Show in event",
        readonly=False,
    )

    is_required = fields.Boolean(
        default=False,
        string="Is required",
        readonly=False
    )

    link = fields.Html(
        string="Link"
    )
