from odoo import api, models
from odoo.exceptions import ValidationError

from ..const import WORDING_REPLACEMENTS


class EventEvent(models.Model):
    _inherit = "event.event"

    @api.model
    def _search_build_dates(self):
        dates = super()._search_build_dates()
        for date_filter in dates:
            date_filter[1] = WORDING_REPLACEMENTS.get(date_filter[1], date_filter[1])
        return dates

    @api.constrains("website_id")
    def _check_website_id(self):
        try:
            return super()._check_website_id()
        except ValidationError as error:
            raise ValidationError(
                WORDING_REPLACEMENTS.get(str(error), str(error))
            ) from error
