import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    responsible_show_on_website = fields.Boolean(
        string="Show Responsible on Website",
        help="Show the responsible person on event page",
    )

    responsible_show_phone_on_website = fields.Boolean(
        string="Show Responsible's Phone on Website",
        help="Show the phone number on event page",
    )

    responsible_show_mobile_on_website = fields.Boolean(
        string="Show Responsible's Mobile on Website",
        help="Show the mobile number on event page",
    )

    responsible_show_email_on_website = fields.Boolean(
        string="Show Responsible's E-mail on Website",
        help="Show the e-mail address on event page",
    )
