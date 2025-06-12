from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

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
