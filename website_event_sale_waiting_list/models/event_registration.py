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
# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
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

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("sale_order_id.state")
    def _compute_registration_status(self):
        """Keep a paid waiting-list confirmation on "wait" until it is paid.

        Core's own computation (event_sale, run first via super()) assigns
        "draft" to any registration whose linked order exists but is not
        yet confirmed as "sale" - correct for an ordinary cart signup, but
        wrong here: the registration was already on the waiting list and
        should keep showing that until the order is actually paid, then
        jump straight to "open".
        """
        super()._compute_registration_status()
        for registration in self.filtered("confirmed_from_waiting_list"):
            if registration.sale_order_id.state == "sale":
                registration.state = "open"
            elif registration.sale_order_id.state != "cancel":
                registration.state = "wait"

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        """Never let a waiting-list registration end up linked to a cart.

        ``website_event_sale``'s own ``_create_attendees_from_registration_post``
        (see that controller) decides whether a ticket needs a sale order
        line, and stamps ``sale_order_id``/``sale_order_line_id`` into
        ``vals`` accordingly, before the registration itself is even
        created - with no way yet to know that
        ``website_event_waiting_list``'s own ``create()`` (run as part of
        the same ``super()`` chain) is about to route this particular
        registration to the waiting list instead. Even a free ticket can
        end up linked this way, since the sale controller only skips the
        cart entirely when the visitor has no cart open at all - a
        leftover one from earlier browsing is enough to trigger it.
        Left alone this makes no sense for a seat that was not actually
        claimed, and confuses ``WebsiteEventSaleController.registration_confirm``
        into redirecting to "/shop/checkout" or "/shop/confirmation"
        instead of this event's own waiting-list confirmation - reusing
        :meth:`_check_waiting_list` here (same method, same ``vals``)
        keeps this decision consistent with that one regardless of which
        of the two ``create()`` overrides actually runs first.
        """
        for vals in vals_list:
            if self._check_waiting_list(vals):
                vals["sale_order_id"] = False
                vals["sale_order_line_id"] = False
        return super().create(vals_list)

    # 7. Action methods
    def action_cancel(self):
        """Send a paid waiting-list registration back to the waiting list.

        website_event_sale calls this on the registrations covering a cart
        quantity decrease (see SaleOrder._cart_update_order_line in that
        module). For an ordinary registration that correctly means
        "cancelled", but for one that came from the waiting list the seat
        was never actually claimed - cancelling it outright would just
        lose the visitor's place in line instead of freeing the seat back
        up for the next person waiting.
        """
        confirmed_waiting = self.filtered("confirmed_from_waiting_list")
        super(EventRegistration, self - confirmed_waiting).action_cancel()
        confirmed_waiting.write(
            {
                "state": "wait",
                "sale_order_id": False,
                "sale_order_line_id": False,
                "confirmed_from_waiting_list": False,
            }
        )

    # 8. Business methods
