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

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    def write(self, vals):
        res = super().write(vals)
        if vals.get("state") in ["sent", "sale", "done"]:
            registrations = self.env["event.registration"].search(
                [("sale_order_id", "in", self.ids)]
            )
            if registrations and registrations._check_auto_confirmation():
                registrations.sudo().action_confirm()
        return res

    # 7. Action methods

    # 8. Business methods


class SaleOrderLine(models.Model):
    # 1. Private attributes
    _inherit = "sale.order.line"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    def _unlink_associated_registrations(self):
        # Do not unlink registration confirmed through waiting list
        # instead move it back to waiting list and remove sale_order
        registrations = self.env["event.registration"].search(
            [
                ("sale_order_line_id", "in", self.ids),
                ("confirmed_from_waiting_list", "=", True),
            ]
        )
        for registration in registrations:
            registration.sudo().write(
                {"sale_order_id": False, "sale_order_line_id": False, "state": "wait"}
            )
        self.env["event.registration"].search(
            [
                ("sale_order_line_id", "in", self.ids),
                ("confirmed_from_waiting_list", "=", False),
            ]
        ).unlink()

    # 7. Action methods

    # 8. Business methods
