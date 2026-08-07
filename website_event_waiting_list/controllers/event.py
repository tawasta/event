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
# 1. Standard library imports:
import logging

# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.website_event.controllers.main import WebsiteEventController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class WebsiteEventControllerWaiting(WebsiteEventController):
    def _prepare_registration_new_values(self, event, **post):
        """Let the attendee-details form render even when sold out.

        Core only shows the ticket/question fields when
        ``availability_check`` is true (see
        ``website_event.registration_attendee_details``); with a waiting
        list enabled, an oversold order should still let the visitor fill
        in their details and submit - :meth:`registration_confirm` and
        ``event.registration.create()`` take care of routing it to the
        waiting list instead of rejecting it.
        """
        values = super()._prepare_registration_new_values(event, **post)
        if values and event.waiting_list:
            values["availability_check"] = True
        return values

    @http.route()
    def registration_confirm(self, event, **post):
        """Let oversold submissions become waiting-list registrations.

        Scopes the seat-overflow bypass (see
        ``event.event._verify_seats_availability``) to this one request via
        context, so it never weakens overselling protection anywhere else.

        Two separate places need the bypass, not just one: core's own
        ``registration_confirm`` explicitly calls ``event._verify_seats_availability``
        first (using the ``event`` argument below), but then creates the
        registrations through ``request.env['event.registration']`` (see
        ``_create_attendees_from_registration_post``), which triggers the
        very same check again as an ``@api.constrains`` during ``create()``
        - through ``request.env``'s own context, not through whatever
        context ``event`` happens to carry. Both ``event`` and
        ``request.env`` are therefore updated here, or the constraint would
        still reject an oversold submission even though the earlier
        explicit check passed.
        """
        if event.waiting_list:
            request.update_context(website_event_waiting_list_bypass_seats_check=True)
            event = event.with_context(
                website_event_waiting_list_bypass_seats_check=True
            )
        return super().registration_confirm(event, **post)

    @http.route(
        ['/event/<model("event.event"):event>/waiting-list/manage/<string:token>'],
        type="http",
        auth="public",
        website=True,
    )
    def waiting_list_manage(self, event, token, **post):
        """Public page to confirm or cancel a waiting-list registration.

        Deliberately independent of ``website_event_cancellation``: its own
        token, route and page, so this module never needs that one
        installed. ``token`` is matched against
        ``waiting_list_access_token`` (this module's own field), not
        against ``website_event_cancellation``'s unrelated
        ``access_token``.

        :param event.event event: event the registration belongs to
        :param str token: the registration's ``waiting_list_access_token``
        """
        registration = event.sudo().registration_ids.filtered(
            lambda r: r.waiting_list_access_token == token
        )
        if not registration:
            return request.render("website.page_404")

        if post:
            new_state = post.get("new_state")
            if new_state == "open" and registration.state == "wait":
                try:
                    registration.sudo().action_waiting_confirm()
                except ValidationError as exc:
                    # Someone else claimed the seat between the email being
                    # sent and this click; fall through to re-render the
                    # page, which will accurately show it is no longer
                    # confirmable instead of a hard error.
                    _logger.info(
                        "Waiting-list confirmation for registration %s rejected: %s",
                        registration.id,
                        exc,
                    )
            elif new_state == "cancel":
                registration.sudo().action_cancel()

        if registration.sudo().state == "done":
            return request.render("website.page_404")

        return request.render(
            "website_event_waiting_list.manage_waiting_registration",
            {"event": event, "registration": registration},
        )
