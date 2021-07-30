from odoo import fields
from odoo import models


class EventEvent(models.Model):
    _inherit = "event.event"

    batch_id = fields.Many2one(string="Batch", comodel_name="op.batch")
