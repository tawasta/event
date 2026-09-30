from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    event_ticket_auto_split_on_post = fields.Boolean(
        string="Split Event Ticket Lines on Invoice Confirmation",
        config_parameter="event_ticket_individual_invoice_lines.auto_split_on_post",
        default=False,
    )
