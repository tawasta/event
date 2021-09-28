from odoo import http
import json
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class PortalCertificate(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "event_count" in counters:
            values['event_count'] = request.env['event.registration'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id)
            ])

        return values

    @http.route(["/my/events"], type="http", auth="user", website=True)
    def portal_my_events(self, **kw):
        values = self._prepare_portal_layout_values()

        registrations = request.env["event.registration"].search(
            [
                ('partner_id', '=', request.env.user.partner_id.id)
            ]
        )

        values.update(
            {
                "registrations": registrations,
                "page_name": "event",
                "default_url": "/my/events",
            }
        )
        return request.render(
            "website_my_events.portal_my_events", values
        )

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
        values = {
        }
        return json.dumps(values)
