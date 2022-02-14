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

import logging

# 1. Standard library imports:
from werkzeug.exceptions import NotFound

# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.website_event_track.controllers.event_track import EventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)


class EventTrackControllerAdvanced(EventTrackController):
    def _get_event_track_proposal_values(self, event):
        user_id = request.env.user
        tracks = request.env["event.track"].search(
            [["user_id", "=", user_id.id], ["event_id", "=", event.id]]
        )
        values = {"tracks": tracks, "event": event}
        return values

    def _get_event_track_proposal_form_values(self, event, **post):
        track_id = post.get("track_id")
        if track_id:
            track = request.env["event.track"].search([["id", "=", track_id]])
        else:
            track = request.env["event.track"]
        track_languages = request.env["res.lang"].search([], order="id")
        values = {"track": track, "track_languages": track_languages, "event": event}
        return values

    def _get_event_track_proposal_post_values(self, event, **post):
        # Application type
        application_type = False
        if post.get("application_type"):
            event_track_type = request.env["event.track.type"].search(
                [("code", "=", post.get("application_type"))], limit=1
            )
            if event_track_type:
                application_type = event_track_type.id
        # Track
        track_values = {
            "name": post.get("track_name"),
            "type": application_type,
            "event_id": event.id,
            "user_id": False,
            "description": post.get("description"),
            "video_url": post.get("video_url"),
            "target_group": post.get("target_group") or False,
            "target_group_info": post.get("target_group_info"),
            "language": post.get("language"),
        }
        values = {"track": track_values}
        return values

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

    @http.route(
        ["""/event/<model("event.event"):event>/track_proposal/form"""],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def event_track_proposal_form(self, event, **post):
        if not event.can_access_from_current_website():
            raise NotFound()

        values = self._get_event_track_proposal_form_values(event, **post)

        return request.env["ir.ui.view"]._render_template(
            "website_event_track_advanced.event_track_application", values
        )

    @http.route(
        ["""/event/<model("event.event"):event>/track_proposal/post"""],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def event_track_proposal_post(self, event, **post):
        if not event.can_access_from_current_website():
            raise NotFound()

        _logger.info("Posted values: %s" % dict(post))
        values = self._get_event_track_proposal_post_values(event, **post)
        _logger.info("Used values: %s" % values)
        request.env["event.track"].sudo().create(values["track"])

        values = self._get_event_track_proposal_values(event)
        return request.render("website_event_track.event_track_proposal", values)
