from odoo import api
from odoo import fields
from odoo import models


class EventEvent(models.Model):
    _inherit = "event.event"

    organizer_id = fields.Many2one(
        default=lambda self: self.env.user.partner_id,
    )

    @api.onchange("user_id")
    def onchange_user_id_update_organizer_id(self):
        for record in self:
            record.organizer_id = record.user_id.partner_id.id
