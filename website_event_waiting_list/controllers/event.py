##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
import werkzeug

# 3. Odoo imports (openerp):
from odoo import fields, http
from odoo.http import request

from odoo.addons.website_event_cancellation.controllers.event import (
    WebsiteEventController,
)

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventControllerWaiting(WebsiteEventController):
    @http.route(
        ['/event/<model("event.event"):event>/registration/new'],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def registration_new(self, event, **post):
        """
        Registration modal and
        Waiting list modal
        """
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        warning_msg = ""
        availability_check = True
        waiting_list_check = post.get("waiting_list_button")
        if waiting_list_check:
            availability_check = False

        tickets = self._process_tickets_form(event, post)
        ordered_seats = 0
        for ticket in tickets:
            ordered_seats += ticket["quantity"]
            if event.seats_limited and ticket.get("ticket"):
                # return error message if trying to register for a ticket that is sold out
                # or trying to join a waiting list for a ticket that is not sold out
                # and event is not sold out
                for event_ticket in ticket.get("ticket"):
                    if (
                        not availability_check
                        and waiting_list_check
                        and (
                            not event_ticket.seats_limited
                            or (
                                event_ticket.seats_limited
                                and event_ticket.seats_available > 0
                            )
                        )
                        and event.seats_available > 0
                    ):
                        warning_msg = (
                            "You tried to join a waiting list for "
                            "a ticket that has available seats"
                        )
                        waiting_list_check = False
                    elif (
                        availability_check
                        and not waiting_list_check
                        and event_ticket.seats_max
                        and event_ticket.seats_available <= 0
                    ):
                        warning_msg = "You tried to order a ticket that is sold out"
                        availability_check = False
            if (
                event.seats_limited
                and event.seats_available < ordered_seats
                and availability_check
                and not waiting_list_check
            ):
                if not warning_msg:
                    warning_msg = "You tried to order more tickets than available seats"
                availability_check = False
        if not tickets:
            return False
        return request.env["ir.ui.view"]._render_template(
            "website_event_waiting_list.registration_attendee_details",
            {
                "tickets": tickets,
                "event": event,
                "availability_check": availability_check,
                "waiting_list_check": waiting_list_check,
                "warning_msg": warning_msg,
            },
        )

    @http.route(
        ["""/event/<model("event.event"):event>/registration/confirm"""],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def registration_confirm(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        registrations = self._process_attendees_form(event, post)
        waiting_list_check = post.get("waiting_list_check")

        # If post was not for waiting_list and trying to register more seats than available
        # Or trying to register more seats for a ticket than available
        # return 404
        for ticket in event.event_ticket_ids:
            ticket_count = 0
            for registration in registrations:
                if ticket.id == registration["event_ticket_id"]:
                    ticket_count += 1
            if (
                not waiting_list_check
                and ticket.seats_max
                and ticket_count > ticket.seats_available
            ):
                return request.render(
                    "website_event_waiting_list.registration_fail",
                    {
                        "warning_msg": "You tried to order more tickets than "
                        "tickets available.",
                        "event": event,
                    },
                )
        if (
            not waiting_list_check
            and event.seats_limited
            and len(registrations) > event.seats_available
        ):
            return request.render(
                "website_event_waiting_list.registration_fail",
                {
                    "warning_msg": "You tried to order more tickets than available seats.",
                    "event": event,
                },
            )

        attendees_sudo = self._create_attendees_from_registration_post(
            event, registrations
        )

        return request.render(
            "website_event.registration_complete",
            self._get_registration_confirm_values(event, attendees_sudo),
        )

    def _process_attendees_form(self, event, form_details):
        """Process data posted from the attendee details form.
        :param form_details: posted data from frontend registration form, like
            {'1-name': 'r', '1-email': 'r@r.com', '1-phone': '', '1-event_ticket_id': '1'}
        """
        allowed_fields = request.env[
            "event.registration"
        ]._get_website_registration_allowed_fields()
        registration_fields = {
            key: v
            for key, v in request.env["event.registration"]._fields.items()
            if key in allowed_fields
        }
        registrations = {}
        global_values = {}
        for key, value in form_details.items():
            # skip loop if key not splittable
            try:
                counter, attr_name = key.split("-", 1)
            except ValueError:
                continue
            field_name = attr_name.split("-")[0]
            if field_name not in registration_fields:
                continue
            elif isinstance(
                registration_fields[field_name], (fields.Many2one, fields.Integer)
            ):
                value = (
                    int(value) or False
                )  # 0 is considered as a void many2one aka False
            else:
                value = value

            if counter == "0":
                global_values[attr_name] = value
            else:
                registrations.setdefault(counter, dict())[attr_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value

        return list(registrations.values())

    @http.route(
        ['/event/<model("event.event"):event>/registration/manage/<string:code>'],
        type="http",
        auth="public",
        website=True,
    )
    def confirm_url_template(self, event, code, **post):
        """
        Return correct confirmation page depending on state
        Confirm state changes on post
        """
        for registration in event.sudo().registration_ids:
            if registration.sudo().access_token == code:
                render_values = {
                    "event": event,
                    "registration": registration,
                    "ticket": registration.event_ticket_id,
                }
                if post:
                    new_state = post.get("new_state")
                    cur_state = post.get("current_state")
                    if (
                        cur_state == "wait"
                        and new_state == "open"
                        and event.sudo().seats_available >= 1
                    ):
                        registration.sudo().write({"state": "open"})
                    if new_state == "cancel":
                        registration.sudo().write({"state": "cancel"})

                if registration.sudo().state in ["wait", "cancel", "open"]:
                    return request.render(
                        "website_event_waiting_list.confirm_waiting", render_values
                    )
        return request.render("website.page_404")
