from odoo import fields, models


class EventType(models.Model):
    _inherit = "event.type"

    name = fields.Char(translate=False)


class EventEvent(models.Model):
    _inherit = "event.event"

    name = fields.Char(translate=False)
    description = fields.Html(translate=False)
