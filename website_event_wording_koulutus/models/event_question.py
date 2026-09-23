from odoo import api, models
from odoo.exceptions import UserError

from ..const import WORDING_REPLACEMENTS


class EventQuestion(models.Model):
    _inherit = "event.question"

    @api.constrains("event_type_id", "event_id")
    def _constrains_event(self):
        try:
            return super()._constrains_event()
        except UserError as error:
            raise UserError(WORDING_REPLACEMENTS.get(str(error), str(error))) from error
