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
from odoo import http
from odoo.http import request

from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController

# 4. Imports from Odoo modules:
from odoo.addons.website_event_waiting_list.controllers.event import (
    WebsiteEventControllerWaiting,
)

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventSaleWaitingListController(
    WebsiteEventSaleController, WebsiteEventControllerWaiting
):
    def _create_attendees_from_registration_post(
        self, event, registration_data, waiting_list_check
    ):
        # we have at least one registration linked to a ticket -> sale mode activate
        if (
            any(info.get("event_ticket_id") for info in registration_data)
            and not waiting_list_check
        ):
            order = request.website.sale_get_order(force_create=1)

        if not waiting_list_check:
            for info in [r for r in registration_data if r.get("event_ticket_id")]:
                ticket = (
                    request.env["event.event.ticket"]
                    .sudo()
                    .browse(info["event_ticket_id"])
                )
                cart_values = order.with_context(
                    event_ticket_id=ticket.id, fixed_price=True
                )._cart_update(product_id=ticket.product_id.id, add_qty=1)
                info["sale_order_id"] = order.id
                info["sale_order_line_id"] = cart_values.get("line_id")

        return super(
            WebsiteEventControllerWaiting, self
        )._create_attendees_from_registration_post(event, registration_data)

    @http.route()
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
            event, registrations, waiting_list_check
        )

        # we have at least one registration linked to a ticket
        # and not in a waiting list -> sale mode activate
        if (
            any(info["event_ticket_id"] for info in registrations)
            and not waiting_list_check
        ):
            order = request.website.sale_get_order(force_create=False)
            if order.amount_total:
                return request.redirect("/shop/checkout")
            # free tickets -> order with amount = 0: auto-confirm, no checkout
            elif order:
                order.action_confirm()  # tde notsure: email sending ?
                request.website.sale_reset()

        return request.render(
            "website_event.registration_complete",
            self._get_registration_confirm_values(event, attendees_sudo),
        )

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
                        if self._confirm_registration_from_waiting_list(registration):
                            registration.sudo().write(
                                {"confirmed_from_waiting_list": True}
                            )
                            return request.redirect("/shop/checkout")
                        else:
                            if registration.event_id.auto_confirm:
                                registration.sudo().write({"state": "open"})
                            else:
                                registration.sudo().write({"state": "draft"})

                    if new_state == "cancel":
                        registration.sudo().write({"state": "cancel"})

                if registration.sudo().state in ["wait", "cancel", "open"]:
                    return request.render(
                        "website_event_waiting_list.confirm_waiting", render_values
                    )
        return request.render("website.page_404")

    def _confirm_registration_from_waiting_list(self, registration):
        if registration.event_ticket_id:
            order = request.website.sale_get_order(force_create=1)
            cart_values = order.with_context(
                event_ticket_id=registration.event_ticket_id.id, fixed_price=True
            )._cart_update(
                product_id=registration.event_ticket_id.product_id.id, add_qty=1
            )
            registration.sudo().write(
                {
                    "sale_order_id": order.id,
                    "sale_order_line_id": cart_values.get("line_id"),
                }
            )
            if order.amount_total:
                return True
            elif order:
                order.action_confirm()
                request.website.sale_reset()
                return False
