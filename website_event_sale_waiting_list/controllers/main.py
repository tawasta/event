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
from odoo.tools import float_is_zero

from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
from odoo.addons.website_event_waiting_list.controllers.event import (
    WebsiteEventControllerWaiting,
)


class WebsiteEventSaleWaitingListController(
    WebsiteEventSaleController, WebsiteEventControllerWaiting
):
    def _create_attendees_from_registration_post(self, event, registration_data):
        """Take the tickets of the registrations that wait out of the cart.

        ``website_event_sale`` adds every ordered ticket to the cart before the
        registrations are created, and some of them are routed to the waiting
        list then. They are not bought now, so the cart must not charge them.
        Once the cart has no tickets left, core goes on to the confirmation
        page of the registration instead of the checkout.
        """
        attendees_sudo = super()._create_attendees_from_registration_post(
            event, registration_data
        )
        self._drop_waiting_tickets_from_cart(attendees_sudo)
        return attendees_sudo

    def _drop_waiting_tickets_from_cart(self, attendees_sudo):
        waiting = attendees_sudo.filtered(lambda attendee: attendee.state == "wait")
        order_sudo = request.cart
        if not waiting or not order_sudo:
            return
        for line in order_sudo.order_line.filtered("event_ticket_id"):
            if not any(
                attendee.event_ticket_id == line.event_ticket_id
                and attendee.event_slot_id == line.event_slot_id
                for attendee in waiting
            ):
                continue
            bought = (
                request.env["event.registration"]
                .sudo()
                .search_count(
                    [("sale_order_line_id", "=", line.id), ("state", "!=", "cancel")]
                )
            )
            if bought < line.product_uom_qty:
                order_sudo._cart_update_line_quantity(line.id, bought)

    @http.route()
    def waiting_list_manage_action(self, event, token, new_state=None, **post):
        """Route a paid-ticket waiting-list confirmation through the cart.

        Only a "claim my seat" submission for a ticket that actually costs
        something is intercepted here; a free or ticket-less registration,
        or a cancel request, fall through unchanged.
        """
        if new_state == "open":
            registration = self._get_waiting_registration(event, token)
            ticket = registration.event_ticket_id
            if (
                registration.state == "wait"
                and registration.waiting_list_to_confirm
                and ticket
                and not float_is_zero(ticket.price, precision_digits=2)
            ):
                return self._confirm_waiting_registration_paid(event, registration)
        return super().waiting_list_manage_action(
            event, token, new_state=new_state, **post
        )

    def _confirm_waiting_registration_paid(self, event, registration):
        """Add the ticket to the visitor's cart and send them to checkout.

        The registration stays ``wait`` until the order is actually paid
        (see ``EventRegistration._compute_registration_status``), so
        following the link never hands out a seat for free. If the ticket
        sold out in the meantime, ``_cart_add`` reports it via an
        empty/zero ``cart_values`` instead of raising - the registration
        is left on the waiting list and the page is shown again.
        """
        if registration.confirmed_from_waiting_list:
            # Already in a cart: adding it again would buy the seat twice
            return request.redirect("/shop/cart")
        order_sudo = request.cart or request.website._create_cart()
        cart_values = order_sudo._cart_add(
            product_id=registration.event_ticket_id.product_id.id,
            quantity=1,
            event_ticket_id=registration.event_ticket_id.id,
            event_slot_id=registration.event_slot_id.id,
        )
        if not cart_values.get("line_id") or cart_values.get("quantity", 0) <= 0:
            return request.redirect(f"{request.httprequest.path}?confirm_failed=1")
        registration.sudo().write(
            {
                "sale_order_id": order_sudo.id,
                "sale_order_line_id": cart_values["line_id"],
                "confirmed_from_waiting_list": True,
            }
        )
        request.session["sale_last_order_id"] = order_sudo.id
        return request.redirect("/shop/checkout?try_skip_step=true")
