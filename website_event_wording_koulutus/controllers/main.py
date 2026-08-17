from odoo.exceptions import UserError

from odoo.addons.website_event.controllers.main import WebsiteEventController

from ..const import WORDING_REPLACEMENTS


class WebsiteEventWordingKoulutusController(WebsiteEventController):
    def _process_attendees_form(self, event, form_details):
        try:
            return super()._process_attendees_form(event, form_details)
        except UserError as error:
            raise UserError(WORDING_REPLACEMENTS.get(str(error), str(error))) from error
