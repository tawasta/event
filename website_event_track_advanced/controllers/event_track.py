##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
from werkzeug.exceptions import NotFound

# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.website_event_track.controllers.event_track import EventTrackController

# 2. Known third party imports:


# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackControllerAdvanced(EventTrackController):
    @http.route(
        ["""/event/<model("event.event"):event>/track_proposal"""],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def event_track_proposal(self, event, **post):
        if not event.can_access_from_current_website():
            raise NotFound()

        values = self._get_event_track_proposal_values(event)
        return request.render("website_event_track.event_track_proposal", values)

    def _get_event_track_proposal_values(self, event):
        user_id = request.env.user
        values = {"error": {}, "error_message": []}
        tracks = request.env["event.track"].search(
            [["user_id", "=", user_id.id], ["event_id", "=", event.id]]
        )
        values.update({"tracks": tracks, "event": event})

        return values
