from odoo import api
from odoo import models


class EventNameWithoutDate(models.Model):
    _inherit = "event.event"

    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for event in self:
            result.append((event.id, '%s' % (event.name)))
            return result
