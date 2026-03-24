from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    registration_info = fields.Text(
        "Registration info", help="Info to be shown before registration"
    )
