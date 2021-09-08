from odoo import fields
from odoo import models


class EventEventTicket(models.Model):
    _inherit = "event.event.ticket"

    batch_id = fields.Many2one(string="Batch", comodel_name="op.batch")
