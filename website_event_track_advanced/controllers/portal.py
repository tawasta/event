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
import babel.dates

# 3. Odoo imports (openerp):
from odoo import fields, http
from odoo.http import request
from odoo.tools.misc import get_lang

# 4. Imports from Odoo modules:
from odoo.addons.portal.controllers.portal import CustomerPortal

# 2. Known third party imports:


# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class PortalTrack(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "track_count" in counters:
            track_count = request.env["event.track"].search_count(
                [("partner_id", "=", request.env.user.partner_id.id)]
            )
            reviewer = request.env.user.reviewer_id
            if reviewer:
                review_track_count = (
                    request.env["event.track"]
                    .sudo()
                    .search_count(
                        [
                            ("partner_id", "!=", request.env.user.partner_id.id),
                            ("review_group.reviewers", "=", reviewer.id),
                            ("stage_id.is_submitted", "=", True),
                        ]
                    )
                )
                track_count += review_track_count
            values["track_count"] = track_count or 0
        return values

    def get_formated_date(self, event):
        start_date = fields.Datetime.from_string(event.date_begin).date()
        end_date = fields.Datetime.from_string(event.date_end).date()
        month = babel.dates.get_month_names(
            "abbreviated", locale=get_lang(event.env).code
        )[start_date.month]
        return ("%s %s%s") % (
            month,
            start_date.strftime("%e"),
            (end_date != start_date and ("-" + end_date.strftime("%e")) or ""),
        )

    @http.route(["/my/tracks"], type="http", auth="user", website=True)
    def portal_my_tracks(self, **kw):
        values = self._prepare_portal_layout_values()
        tracks = (
            request.env["event.track"]
            .sudo()
            .search([("partner_id", "=", request.env.user.partner_id.id)])
        )
        reviewer = request.env.user.reviewer_id
        if reviewer:
            review_tracks = (
                request.env["event.track"]
                .sudo()
                .search(
                    [
                        ("partner_id", "!=", request.env.user.partner_id.id),
                        ("review_group.reviewers", "=", reviewer.id),
                        ("stage_id.is_submitted", "=", True),
                    ]
                )
            )
            values.update({"review_tracks": review_tracks or False})

        track_languages = request.env["res.lang"].search([], order="id")
        values.update(
            {
                "tracks": tracks,
                "page_name": "track",
                "default_url": "/my/tracks",
                "get_formated_date": self.get_formated_date,
                "track_languages": track_languages,
                'event': False,
            }
        )
        return request.render("website_event_track_advanced.portal_my_tracks", values)
