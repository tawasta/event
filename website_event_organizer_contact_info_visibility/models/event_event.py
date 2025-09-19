import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    organizer_show_on_website = fields.Boolean(
        string="Show Organizer on Website",
        help="Show the organizer on event page",
        default=True,
    )

    organizer_show_phone_on_website = fields.Boolean(
        string="Show Organizer's Phone on Website",
        help="Show the phone number on event page",
        default=True,
    )

    organizer_show_mobile_on_website = fields.Boolean(
        string="Show Organizer's Mobile on Website",
        help="Show the mobile number on event page",
        default=True,
    )

    organizer_show_email_on_website = fields.Boolean(
        string="Show Organizer's E-mail on Website",
        help="Show the e-mail address on event page",
        default=True,
    )
