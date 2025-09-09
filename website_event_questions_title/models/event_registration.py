from odoo import fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    title = fields.Char()
