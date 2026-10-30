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
from odoo import http
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventControllerCancel(WebsiteEventController):
    def _get_registration_by_token(self, event, token):
        """Return the registration of this event that owns the access token.

        sudo: the visitor is usually public and cannot read registrations, the
        unguessable token from the emailed link is the proof of access.
        """
        return (
            request.env["event.registration"]
            .sudo()
            .search(
                [("event_id", "=", event.id), ("access_token", "=", token)], limit=1
            )
        )

    @http.route(
        ['/event/<model("event.event"):event>/registration/manage/<string:token>'],
        type="http",
        auth="public",
        methods=["GET"],
        website=True,
        sitemap=False,
        readonly=True,
    )
    def registration_manage(self, event, token, **post):
        """Show the registration and, when allowed, the cancel button."""
        registration = self._get_registration_by_token(event, token)
        if not registration:
            return request.not_found()
        return request.render(
            "website_event_cancellation.cancel_registration",
            {
                "event": event,
                "registration": registration,
                "ticket": registration.event_ticket_id,
            },
        )

    @http.route(
        ['/event/<model("event.event"):event>/registration/manage/<string:token>'],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def registration_manage_cancel(self, event, token, **post):
        """Cancel the registration. State changes only on POST (CSRF protected)."""
        registration = self._get_registration_by_token(event, token)
        if not registration:
            return request.not_found()
        # Rules are enforced here, not only by hiding the button in the template
        if registration.able_to_cancel:
            registration.action_cancel()
        # Redirect so a page reload does not resubmit the form
        return request.redirect(request.httprequest.path)
