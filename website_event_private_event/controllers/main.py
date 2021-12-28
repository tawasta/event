##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
from odoo import fields, http
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.website_event.controllers.main import WebsiteEventController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventControllerPrivateEvent(WebsiteEventController):
    @http.route(
        "/event/get_country_event_list", type="json", auth="public", website=True
    )
    def get_country_events(self, **post):
        Event = request.env["event.event"]
        country_code = request.session["geoip"].get("country_code")
        result = {"events": [], "country": False}
        events = None
        domain = request.website.website_domain()
        if country_code:
            country = request.env["res.country"].search(
                [("code", "=", country_code)], limit=1
            )
            events = Event.search(
                domain
                + [
                    "|",
                    ("address_id", "=", None),
                    ("country_id.code", "=", country_code),
                    ("date_begin", ">=", "%s 00:00:00" % fields.Date.today()),
                    ("is_private_event", "=", False),
                ],
                order="date_begin",
            )
        if not events:
            events = Event.search(
                domain
                + [
                    ("date_begin", ">=", "%s 00:00:00" % fields.Date.today()),
                    ("is_private_event", "=", False),
                ],
                order="date_begin",
            )
        for event in events:
            if country_code and event.country_id.code == country_code:
                result["country"] = country
            result["events"].append(
                {
                    "date": self.get_formated_date(event),
                    "event": event,
                    "url": event.website_url,
                }
            )
        return request.env["ir.ui.view"]._render_template(
            "website_event.country_events_list", result
        )
