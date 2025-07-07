from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    payment_button_text = fields.Char(
        string="Event Payment Button Text", translate=True
    )

    registration_button_text = fields.Char(
        string="Event Registration Button Text", translate=True
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    event_payment_button_text = fields.Char(
        string="Event Payment Button Text",
        related="website_id.payment_button_text",
        readonly=False,
        help="Enter a custom label for the "
        "'Go to Payment' button shown during event registration.",
    )

    event_registration_button_text = fields.Char(
        string="Event Registration Button Text",
        related="website_id.registration_button_text",
        readonly=False,
        help="Enter a custom label for the 'Confirm Registration' "
        "button shown during event registration.",
    )
