import json

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalEvents(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "event_count" in counters:
            values["event_count"] = request.env["event.event"].search_count(
                [("user_id", "=", request.env.user.id)]
            )

        return values

    @http.route(["/my/events"], type="http", auth="user", website=True)
    def portal_my_events(self, **kw):
        values = self._prepare_portal_layout_values()

        events = request.env["event.event"].search(
            [("user_id", "=", request.env.user.id)]
        )

        values.update(
            {
                "events": events,
                "page_name": "event",
                "default_url": "/my/events",
            }
        )
        return request.render("event_feedback_survey.portal_my_events", values)
