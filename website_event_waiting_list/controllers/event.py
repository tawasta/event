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
import werkzeug

# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController

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
        # Tarkista löytyykö 'waiting_list_registration' postista
        waiting_list_check = False
        if "waiting_list_registration" in post:
            # Kutsu alkuperäistä metodia muokatuilla parametreilla
            tickets = self._process_tickets_form(event, post)
            availability_check = True
            if event.seats_limited:
                ordered_seats = 0
                for ticket in tickets:
                    ordered_seats += ticket["quantity"]
                if event.seats_available < ordered_seats:
                    availability_check = False
            if not tickets:
                return False
            default_first_attendee = {}
            if not request.env.user._is_public():
                default_first_attendee = {
                    "name": request.env.user.name,
                    "email": request.env.user.email,
                    "phone": request.env.user.mobile or request.env.user.phone,
                }
            else:
                visitor = request.env["website.visitor"]._get_visitor_from_request()
                if visitor.email:
                    default_first_attendee = {
                        "name": visitor.display_name,
                        "email": visitor.email,
                        "phone": visitor.mobile,
                    }

            if post.get("waiting_list_registration"):
                # availability_check = True
                waiting_list_check = True

            logging.info("====availability_check=====")
            logging.info(availability_check)
            return request.env["ir.ui.view"]._render_template(
                "website_event.registration_attendee_details",
                {
                    "tickets": tickets,
                    "event": event,
                    "availability_check": availability_check,
                    "waiting_list_check": waiting_list_check,
                    "default_first_attendee": default_first_attendee,
                },
            )
        else:
            # Kutsu alkuperäistä metodia normaalisti
            return super().registration_new(event, **post)

    @http.route(
        ["""/event/<model("event.event"):event>/registration/confirm"""],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def registration_confirm(self, event, **post):
        """Check before creating and finalize the creation of the registrations
        that we have enough seats for all selected tickets.
        If we don't, the user is instead redirected to page to register with a
        formatted error message."""
        registrations_data = self._process_attendees_form(event, post)
        event_ticket_ids = {
            registration["event_ticket_id"] for registration in registrations_data
        }
        event_tickets = request.env["event.event.ticket"].browse(event_ticket_ids)
        if not event.waiting_list and any(
            event_ticket.seats_limited
            and event_ticket.seats_available < len(registrations_data)
            for event_ticket in event_tickets
        ):
            return request.redirect(
                "/event/%s/register?registration_error_code=insufficient_seats"
                % event.id
            )
        attendees_sudo = self._create_attendees_from_registration_post(
            event, registrations_data
        )
        return request.redirect(
            ("/event/%s/registration/success?" % event.id)
            + werkzeug.urls.url_encode(
                {"registration_ids": ",".join([str(id) for id in attendees_sudo.ids])}
            )
        )

    # def _process_attendees_form(self, event, form_details):
    #     """Process data posted from the attendee details form.
    #     :param form_details: posted data from frontend registration form, like
    #         {'1-name': 'r', '1-email': 'r@r.com', '1-phone': '', '1-event_ticket_id': '1'}
    #     """
    #     allowed_fields = request.env[
    #         "event.registration"
    #     ]._get_website_registration_allowed_fields()
    #     registration_fields = {
    #         key: v
    #         for key, v in request.env["event.registration"]._fields.items()
    #         if key in allowed_fields
    #     }
    #     registrations = {}
    #     global_values = {}
    #     for key, value in form_details.items():
    #         # skip loop if key not splittable
    #         try:
    #             counter, attr_name = key.split("-", 1)
    #         except ValueError:
    #             continue
    #         field_name = attr_name.split("-")[0]
    #         if field_name not in registration_fields:
    #             continue
    #         elif isinstance(
    #             registration_fields[field_name], (fields.Many2one, fields.Integer)
    #         ):
    #             value = (
    #                 int(value) or False
    #             )  # 0 is considered as a void many2one aka False
    #         else:
    #             value = value

    #         if counter == "0":
    #             global_values[attr_name] = value
    #         else:
    #             registrations.setdefault(counter, dict())[attr_name] = value
    #     for key, value in global_values.items():
    #         for registration in registrations.values():
    #             registration[key] = value

    #     return list(registrations.values())

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
                        registration.sudo().action_cancel()

                if registration.sudo().state in ["wait", "cancel", "open"]:
                    return request.render(
                        "website_event_waiting_list.confirm_waiting", render_values
                    )
        return request.render("website.page_404")
