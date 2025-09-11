from odoo import fields, models


class PrivacyActivity(models.Model):
    _inherit = "privacy.activity"

    show_in_event = fields.Boolean(default=False, readonly=False)
    is_required = fields.Boolean(default=False, readonly=False)
    link_name = fields.Char()
    link = fields.Char(string="Link (URL)")
