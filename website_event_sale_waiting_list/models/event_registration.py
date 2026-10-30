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
from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    confirmed_from_waiting_list = fields.Boolean(
        readonly=True,
        copy=False,
        help="Set while a waiting-list registration is linked to a sale "
        "order for its ticket payment. Distinguishes it from an ordinary "
        "cart signup so its state can be kept as 'wait' until the order "
        "is actually paid (see _compute_registration_status) and so it "
        "can be sent back to the waiting list rather than lost if that "
        "order is cancelled or the ticket removed from the cart (see "
        "action_cancel and SaleOrder._action_cancel).",
    )

    @api.depends("sale_order_id.state")
    def _compute_registration_status(self):
        """Keep a paid waiting-list confirmation on "wait" until it is paid.

        Core's own computation assigns "draft" to any registration with an
        unconfirmed order - correct for an ordinary cart signup, but wrong
        here: it should keep showing "wait" until actually paid.
        """
        res = super()._compute_registration_status()
        for registration in self.filtered("confirmed_from_waiting_list"):
            if registration.sale_order_id.state == "sale":
                registration.state = "open"
            elif registration.sale_order_id.state != "cancel":
                registration.state = "wait"
        return res

    def _route_overflow_to_waiting_list(self, vals_list):
        """Never let a waiting-list registration end up linked to a cart.

        ``website_event_sale``'s controller stamps ``sale_order_id``/
        ``sale_order_line_id`` into ``vals`` before the registration is
        created, with no way yet to know it is about to be routed to the
        waiting list instead - even a free ticket can get linked this way
        if the visitor has a leftover cart open. The links are cleared right
        after the routing has decided, so no other ``create()`` override can
        decide differently.
        """
        res = super()._route_overflow_to_waiting_list(vals_list)
        for vals in vals_list:
            if vals.get("state") == "wait":
                vals["sale_order_id"] = False
                vals["sale_order_line_id"] = False
        return res

    def action_cancel(self):
        """Send a paid waiting-list registration back to the waiting list.

        Only when the ticket leaves the cart: ``website_event_sale`` cancels the
        registrations of a cart line whose quantity decreases (see
        ``SaleOrder._cart_update_order_line``). Correct as "cancelled" for an
        ordinary registration, but a seat claimed from the waiting list was
        never really taken - send it back instead of losing the visitor's place
        in line. Any other cancelling really cancels.
        """
        if not self.env.context.get("waiting_list_cart_update"):
            return super().action_cancel()
        confirmed_waiting = self.filtered("confirmed_from_waiting_list")
        res = super(EventRegistration, self - confirmed_waiting).action_cancel()
        confirmed_waiting.write(
            {
                "state": "wait",
                "sale_order_id": False,
                "sale_order_line_id": False,
                "confirmed_from_waiting_list": False,
            }
        )
        return res

    def action_waiting_cancel(self):
        """The attendee leaves the waiting list: the ticket leaves the cart too."""
        in_cart = self.filtered("confirmed_from_waiting_list")
        lines_in_cart = [
            (registration.sale_order_id, registration.sale_order_line_id)
            for registration in in_cart
            if registration.sale_order_id.state == "draft"
        ]
        in_cart.write(
            {
                "sale_order_id": False,
                "sale_order_line_id": False,
                "confirmed_from_waiting_list": False,
            }
        )
        res = super().action_waiting_cancel()
        # The links are cleared first, so the cart does not cancel the registration
        for order, line in lines_in_cart:
            order._cart_update_line_quantity(line.id, line.product_uom_qty - 1)
        return res
