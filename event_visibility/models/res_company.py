from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    event_hide_badge_fields = fields.Boolean(
        string="Hide Event Badge Fields"
    )
    event_hide_feedback_fields = fields.Boolean(
        string="Hide Event Feedback Fields"
    )
    event_hide_create_partner = fields.Boolean(
        string="Hide Create Partner"
    )

    event_hide_registration_desk = fields.Boolean(
        string="Hide Registration Desk"
    )