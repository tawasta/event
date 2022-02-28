from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    event_sender_address = fields.Char(
        string="Event sender address", config_parameter="event_sender_address"
    )
