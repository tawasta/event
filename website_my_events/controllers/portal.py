from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import json

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class PortalEvent(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "event_count" in counters:
            event_model = request.env["event.registration"]
            event_count = (
                event_model.search_count([])
                if event_model.check_access_rights("read", raise_exception=False)
                else 0
            )
            values["event_count"] = event_count
        return values

    @http.route(
        ["/my/events"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_events(
        self, **kw
    ):
        values = self._prepare_portal_layout_values()
        event_obj = request.env["event.registration"]
        # Avoid error if the user does not have access.
        if not event_obj.check_access_rights("read", raise_exception=False):
            return request.redirect("/my")

        registrations = (
            request.env["event.registration"]
            .sudo()
            .search([("partner_id", "=", request.env.user.partner_id.id)])
        )
        values.update(
            {
                "registrations": registrations,
                "page_name": "Events",
                "default_url": "/my/events",
            }
        )
        return request.render("website_my_events.portal_my_events", values)

    @http.route(
        ["/registration/cancel/<int:registration_id>"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def cancel_registration(self, registration_id=None, **post):
        registration = (
            request.env["event.registration"]
            .sudo()
            .search([("id", "=", registration_id)])
        )
        registration.sudo().action_cancel()
        values = {}
        return json.dumps(values)
