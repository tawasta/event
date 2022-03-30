from odoo import fields, models


class PrivacyActivity(models.Model):
    _inherit = "privacy.activity"

    show_in_event = fields.Boolean(
        default=False, string="Show in event", readonly=False
    )
    is_required = fields.Boolean(default=False, string="Is required", readonly=False)
    link_name = fields.Char(string="Link Name")
    link = fields.Char(string="Link (URL)")
