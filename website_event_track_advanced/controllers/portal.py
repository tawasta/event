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

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http

# 4. Imports from Odoo modules:
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class PortalTrack(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "track_count" in counters:
            track_count = request.env["event.track"].search_count(
                [("partner_id", "=", request.env.user.partner_id.id)]
            )
            values["track_count"] = track_count or 0
        return values

    @http.route(["/my/tracks"], type="http", auth="user", website=True)
    def portal_my_tracks(self, **kw):
        values = self._prepare_portal_layout_values()
        tracks = request.env["event.track"].search(
            [("partner_id", "=", request.env.user.partner_id.id)]
        )
        values.update(
            {"tracks": tracks, "page_name": "track", "default_url": "/my/tracks"}
        )
        return request.render("website_event_track_advanced.portal_my_tracks", values)
