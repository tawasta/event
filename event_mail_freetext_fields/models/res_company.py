from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    show_freetext_confirmation_field = fields.Boolean(
        label="Event Mails: Enable Confirmation Message Additional Text Field",
        default=True,
        help="Shows the field to users on event form.",
    )

    show_freetext_welcome_field = fields.Boolean(
        label="Event Mails: Enable Welcome Message Additional Text Field",
        default=True,
        help="Shows the field to users on event form.",
    )

    show_freetext_reminder_field = fields.Boolean(
        label="Event Mails: Enable Reminder Message Additional Text Field",
        default=True,
        help="Shows the field to users on event form.",
    )

    show_freetext_thankyou_field = fields.Boolean(
        label="Event Mails: Enable Thank you Message Additional Text Field",
        default=True,
        help="Shows the field to users on event form.",
    )
