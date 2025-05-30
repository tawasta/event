from odoo import models, fields


class EventEvent(models.Model):
    _inherit = "event.event"

    freetext_welcome = fields.Html(
        string="Welcome Message: Additional Text",
        help="Additional text that can be embedded into e-mail templates",
    )

    freetext_thankyou = fields.Html(
        string="Thank You Message: Additional Text",
        help="Additional text that can be embedded into e-mail templates",
    )
