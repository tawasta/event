from odoo import fields, models


class EventTemplateTicket(models.Model):
    _inherit = "event.type.ticket"

    name = fields.Char(translate=False)
    description = fields.Text(translate=False)
