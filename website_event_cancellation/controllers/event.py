##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:

# 2. Known third party imports:


# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventControllerCancel(WebsiteEventController):
    @http.route(
        ['/event/<model("event.event"):event>/registration/manage/<string:code>'],
        type="http",
        auth="public",
        website=True,
    )
    def confirm_url_template(self, event, code, **post):
        """
        Return registration managements page and
        Confirm state changes on post
        """
        for registration in event.sudo().registration_ids:
            if registration.sudo().access_token == code:
                render_values = {
                    "event": event,
                    "registration": registration,
                    "ticket": registration.event_ticket_id,
                }
                if post:
                    new_state = post.get("new_state")
                    if new_state == "cancel":
                        registration.sudo().action_cancel()

                if registration.sudo().state not in ["done"]:
                    return request.render(
                        "website_event_cancellation.cancel_registration", render_values
                    )
        return request.render("website.page_404")
