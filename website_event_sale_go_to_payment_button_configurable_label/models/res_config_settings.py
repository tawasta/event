from odoo import models, fields

class Website(models.Model):
    _inherit = 'website'

    payment_button_text = fields.Char(
        string="Event Payment Button Text",
        translate=True
    )

    registration_button_text = fields.Char(
        string="Event Registration Button Text",
        translate=True
    )

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    event_payment_button_text = fields.Char(
        string="Event Payment Button Text",
        related='website_id.payment_button_text',
        readonly=False
    )

    event_registration_button_text = fields.Char(
        string="Event Registration Button Text",
        related='website_id.registration_button_text',
        readonly=False
    )
