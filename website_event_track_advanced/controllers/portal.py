import logging
from itertools import groupby

import babel.dates

from odoo import fields, http
from odoo.http import request
from odoo.tools.misc import get_lang

from odoo.addons.portal.controllers.portal import CustomerPortal


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
        return ("{} {}{}").format(
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
            .search(
                [("partner_id", "=", request.env.user.partner_id.id)], order="event_id"
            )
        )

        grouped_tracks = {}
        for event, tracks_in_event in groupby(tracks, key=lambda track: track.event_id):
            grouped_tracks[event] = list(tracks_in_event)

        values.update(
            {
                "grouped_tracks": grouped_tracks,
                "page_name": "track",
                "default_url": "/my/tracks",
                "get_formated_date": self.get_formated_date,
            }
        )
        reviewer = request.env.user.reviewer_id
        logging.info("===ON ARVIOIJA====")
        if reviewer:
            review_tracks = (
                request.env["event.track"]
                .sudo()
                .search(
                    [
                        ("partner_id", "!=", request.env.user.partner_id.id),
                        ("review_group.reviewers", "=", reviewer.id),
                        ("stage_id.is_submitted", "=", True),
                    ],
                    order="event_id",
                )
            )
            logging.info(review_tracks)
            grouped_review_tracks = {}
            for event, review_tracks_in_event in groupby(
                review_tracks, key=lambda track: track.event_id
            ):
                grouped_review_tracks[event] = list(review_tracks_in_event)

            values.update({"grouped_review_tracks": grouped_review_tracks})

        return request.render("website_event_track_advanced.portal_my_tracks", values)
