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
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update_order_line(self, order_line, quantity, **kwargs):
        """Mark the cart changes, so a confirmation that the cart drops goes back
        to the waiting list (see ``EventRegistration.action_cancel``)."""
        return super(
            SaleOrder, self.with_context(waiting_list_cart_update=True)
        )._cart_update_order_line(order_line, quantity, **kwargs)

    def _action_cancel(self):
        """Send paid waiting-list confirmations back to the waiting list.

        Core's own compute marks every registration on a cancelled order
        as "cancelled" - correct for an ordinary purchase, but a seat
        claimed from the waiting list was never really taken, so it goes
        back to "wait" instead, with the order link cleared. The seats of the
        other registrations are freed, so the waiting list is told.
        """
        # sudo: whoever cancels an order (a salesman) may not see registrations
        registrations = (
            self.env["event.registration"]
            .sudo()
            .search([("sale_order_id", "in", self.ids)])
        )
        waiting_registrations = registrations.filtered("confirmed_from_waiting_list")
        res = super()._action_cancel()
        waiting_registrations.write(
            {
                "state": "wait",
                "sale_order_id": False,
                "sale_order_line_id": False,
                "confirmed_from_waiting_list": False,
            }
        )
        # The cancelled state is computed by core, which does not write it
        registrations.event_id._trigger_mail_scheduler_cron()
        return res
