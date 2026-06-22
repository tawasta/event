from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    hide_badge_fields = fields.Boolean(
        related="company_id.event_hide_badge_fields",
        readonly=True,
    )

    hide_feedback_fields = fields.Boolean(
        related="company_id.event_hide_feedback_fields",
        readonly=True,
    )

    hide_create_partner = fields.Boolean(
        related="company_id.event_hide_create_partner",
        readonly=True,
    )

    hide_registration_desk = fields.Boolean(
        related="company_id.event_hide_registration_desk",
        readonly=True,
    )
