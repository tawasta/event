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
# 2. Known third party imports:
import werkzeug

# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request
from odoo.tools import float_is_zero

# 4. Imports from Odoo modules:
from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
from odoo.addons.website_event_waiting_list.controllers.event import (
    WebsiteEventControllerWaiting,
)

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventSaleWaitingListController(
    WebsiteEventSaleController, WebsiteEventControllerWaiting
):
    @http.route()
    def registration_confirm(self, event, **post):
        """Never let the cart/checkout redirect swallow a waiting-list join.

        ``WebsiteEventSaleController`` sits ahead of
        ``WebsiteEventControllerWaiting`` in the MRO, so its own redirect to
        "/shop/checkout" or "/shop/confirmation" (whenever the cart holds a
        ticket line, even a free one from a leftover cart) silently wins
        over the waiting-list-aware one. Rebuilt here, core-style, whenever
        any registration from this request ended up ``wait`` - see
        :meth:`_create_attendees_from_registration_post` for how they are
        recovered.
        """
        res = super().registration_confirm(event, **post)
        attendees_sudo = getattr(
            request, "website_event_waiting_list_new_attendees", None
        )
        if attendees_sudo and attendees_sudo.filtered(lambda r: r.state == "wait"):
            return request.redirect(
                (f"/event/{event.id}/registration/success?")
                + werkzeug.urls.url_encode(
                    {"registration_ids": ",".join(str(i) for i in attendees_sudo.ids)}
                )
            )
        return res

    def _create_attendees_from_registration_post(self, event, registration_data):
        """Stash the created attendees so :meth:`registration_confirm` can
        tell whether any of them ended up on the waiting list, regardless
        of what the sale controller's own cart-based redirect logic
        decides afterwards.
        """
        attendees_sudo = super()._create_attendees_from_registration_post(
            event, registration_data
        )
        request.website_event_waiting_list_new_attendees = attendees_sudo
        return attendees_sudo

    @http.route()
    def waiting_list_manage(self, event, token, **post):
        """Route a paid-ticket waiting-list confirmation through the cart.

        Only a "claim my seat" submission for a ticket that actually costs
        something is intercepted here; a free or ticket-less registration,
        or a cancel request, fall through unchanged.
        """
        if post.get("new_state") == "open":
            registration = event.sudo().registration_ids.filtered(
                lambda r: r.waiting_list_access_token == token and r.state == "wait"
            )
            ticket = registration.event_ticket_id
            if (
                registration
                and registration.waiting_list_to_confirm
                and ticket
                and not float_is_zero(ticket.price, precision_digits=2)
            ):
                return self._confirm_waiting_registration_paid(event, registration)
        return super().waiting_list_manage(event, token, **post)

    def _confirm_waiting_registration_paid(self, event, registration):
        """Add the ticket to the visitor's cart and send them to checkout.

        The registration stays ``wait`` until the order is actually paid
        (see ``EventRegistration._compute_registration_status``), so
        following the link never hands out a seat for free. If the ticket
        sold out in the meantime, ``_cart_add`` reports it via an
        empty/zero ``cart_values`` instead of raising - the registration
        is left on the waiting list and the same page re-rendered.
        """
        order_sudo = request.cart or request.website._create_cart()
        cart_values = order_sudo._cart_add(
            product_id=registration.event_ticket_id.product_id.id,
            quantity=1,
            event_ticket_id=registration.event_ticket_id.id,
            event_slot_id=registration.event_slot_id.id,
        )
        if not cart_values.get("line_id") or cart_values.get("quantity", 0) <= 0:
            return request.render(
                "website_event_waiting_list.manage_waiting_registration",
                {"event": event, "registration": registration},
            )

        registration.sudo().write(
            {
                "sale_order_id": order_sudo.id,
                "sale_order_line_id": cart_values["line_id"],
                "confirmed_from_waiting_list": True,
            }
        )
        request.session["sale_last_order_id"] = order_sudo.id
        return request.redirect("/shop/checkout?try_skip_step=true")
