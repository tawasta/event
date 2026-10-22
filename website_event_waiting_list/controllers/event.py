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
import logging
from collections import Counter

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController

from ..models.event_event import BYPASS_SEATS_CHECK_CONTEXT_KEY

_logger = logging.getLogger(__name__)


class WebsiteEventControllerWaiting(WebsiteEventController):
    def _prepare_registration_new_values(self, event, **post):
        """Let the attendee-details form render also for more than the free seats.

        Core stops an order that is bigger than the seats left. With a waiting
        list the seats left do not limit the order: the registrations that do not
        fit wait. The order is capped by the total seats and the limit per order
        (see ``event.event._get_waiting_list_order_limit``).
        """
        values = super()._prepare_registration_new_values(event, **post)
        if values and event.waiting_list:
            values["availability_check"] = True
            values["limit_check"] = not any(
                order["quantity"] > event._get_waiting_list_order_limit(order["ticket"])
                for order in values["tickets"]
            )
        return values

    def _exceeds_waiting_list_order_limit(self, event, form_details):
        """Whether the submitted attendees are more than the limit per order.

        The seats no longer limit an order of a waiting-list event, so the number
        of registrations one submission can create is capped here. The numbers
        come from the browser, which cannot be trusted.
        """
        count_per_ticket = Counter(
            data.get("event_ticket_id")
            for data in self._process_attendees_form(event, form_details)
        )
        tickets = (
            request.env["event.event.ticket"]
            .sudo()
            .browse([ticket_id for ticket_id in count_per_ticket if ticket_id])
        )
        return any(
            count > event._get_waiting_list_order_limit(tickets.browse(ticket_id))
            for ticket_id, count in count_per_ticket.items()
        )

    @http.route()
    def registration_confirm(self, event, **post):
        """Let oversold submissions become waiting-list registrations.

        Only the first check of core, that stops an order bigger than the seats
        left, is skipped (see ``event.event._verify_seats_availability``). The
        registrations are created without the flag: the ones that do not fit
        are created as waiting, and the check of core guards the rest.
        """
        if event.waiting_list:
            if self._exceeds_waiting_list_order_limit(event, post):
                return request.redirect(
                    f"/event/{event.id}/register?registration_error_code=insufficient_seats"
                )
            event = event.with_context(**{BYPASS_SEATS_CHECK_CONTEXT_KEY: True})
        return super().registration_confirm(event, **post)

    def _get_registration_confirm_values(self, event, attendees_sudo):
        """Tell the confirmation page which of the registrations are waiting.

        The waiting ones get no tickets, so they are left out of ``attendees``.
        """
        values = super()._get_registration_confirm_values(event, attendees_sudo)
        waiting = attendees_sudo.filtered(lambda r: r.state == "wait")
        values["attendees"] = attendees_sudo - waiting
        values["waiting_attendees"] = waiting
        values["all_waiting"] = bool(waiting) and waiting == attendees_sudo
        return values

    def _get_waiting_registration(self, event, token):
        """Return the registration of this event that owns the token, or nothing.

        sudo: the visitor is usually public and cannot read registrations, the
        unguessable token from the emailed link is the proof of access.
        """
        return (
            request.env["event.registration"]
            .sudo()
            .search(
                [
                    ("event_id", "=", event.id),
                    ("waiting_list_access_token", "=", token),
                ],
                limit=1,
            )
        )

    @http.route(
        ['/event/<model("event.event"):event>/waiting-list/manage/<string:token>'],
        type="http",
        auth="public",
        methods=["GET"],
        website=True,
        sitemap=False,
        readonly=True,
    )
    def waiting_list_manage(self, event, token, confirm_failed=None, **post):
        """Public page to confirm or cancel a waiting-list registration.

        Deliberately independent of ``website_event_cancellation``: own
        token, route and page, so this module never needs that one
        installed.
        """
        registration = self._get_waiting_registration(event, token)
        if not registration:
            return request.not_found()
        return request.render(
            "website_event_waiting_list.manage_waiting_registration",
            {
                # The event of the registration comes from sudo: an event that is
                # not published cannot be read by the public visitor
                "event": registration.event_id,
                "registration": registration,
                "confirm_failed": bool(confirm_failed),
            },
        )

    @http.route(
        ['/event/<model("event.event"):event>/waiting-list/manage/<string:token>'],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def waiting_list_manage_action(self, event, token, new_state=None, **post):
        """Confirm or cancel the waiting registration. Only POST changes the state."""
        registration = self._get_waiting_registration(event, token)
        if not registration:
            return request.not_found()
        confirm_failed = False
        # Only a registration on the waiting list can be changed from here
        if registration.state == "wait":
            if new_state == "open":
                confirm_failed = not self._confirm_waiting_registration(registration)
            elif new_state == "cancel":
                registration.action_waiting_cancel()
        # Redirect so a page reload does not resubmit the form
        path = request.httprequest.path
        return request.redirect(f"{path}?confirm_failed=1" if confirm_failed else path)

    def _confirm_waiting_registration(self, registration):
        """Confirm the registration. Returns whether it succeeded."""
        try:
            with request.env.cr.savepoint():
                registration.action_waiting_confirm()
        except ValidationError as exc:
            # Someone else took the seat between the email being sent and this
            # click. The page shows it is no longer confirmable.
            _logger.info(
                "Waiting-list confirmation of registration %s rejected: %s",
                registration.id,
                exc,
            )
            return False
        return True
