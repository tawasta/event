from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    show_freetext_confirmation_field = fields.Boolean(
        related="company_id.show_freetext_confirmation_field"
    )

    show_freetext_welcome_field = fields.Boolean(
        related="company_id.show_freetext_welcome_field"
    )

    show_freetext_reminder_field = fields.Boolean(
        related="company_id.show_freetext_reminder_field"
    )

    show_freetext_thankyou_field = fields.Boolean(
        related="company_id.show_freetext_thankyou_field"
    )

    freetext_confirmation = fields.Html(
        string="Confirmation Message: Additional Text",
        translate=True,
        help="Additional text that can be embedded into e-mail templates",
    )

    freetext_welcome = fields.Html(
        string="Welcome Message: Additional Text",
        translate=True,
        help="Additional text that can be embedded into e-mail templates",
    )

    freetext_reminder = fields.Html(
        string="Reminder Message: Additional Text",
        translate=True,
        help="Additional text that can be embedded into e-mail templates",
    )

    freetext_thankyou = fields.Html(
        string="Thank You Message: Additional Text",
        translate=True,
        help="Additional text that can be embedded into e-mail templates",
    )
