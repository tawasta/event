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
from odoo import models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class SaleOrder(models.Model):
    # 1. Private attributes
    _inherit = "sale.order"

    # 8. Business methods
    def _action_cancel(self):
        """Send paid waiting-list confirmations back to the waiting list.

        Core's own compute marks every registration on a cancelled order
        as "cancelled" - correct for an ordinary purchase, but a seat
        claimed from the waiting list was never really taken, so it goes
        back to "wait" instead, with the order link cleared.
        """
        waiting_registrations = self.env["event.registration"].search(
            [
                ("sale_order_id", "in", self.ids),
                ("confirmed_from_waiting_list", "=", True),
            ]
        )
        res = super()._action_cancel()
        waiting_registrations.write(
            {
                "state": "wait",
                "sale_order_id": False,
                "sale_order_line_id": False,
                "confirmed_from_waiting_list": False,
            }
        )
        return res
