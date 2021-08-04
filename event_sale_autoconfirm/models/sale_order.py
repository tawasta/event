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

# 3. Odoo imports (openerp):
from odoo import api, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class SaleOrderLine(models.Model):
    # 1. Private attributes
    _inherit = "sale.order.line"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.multi
    def _update_registrations(
        self, confirm=True, cancel_to_draft=False, registration_data=None
    ):
        """ Create or update registrations linked to a sales order line. A sale
        order line has a product_uom_qty attribute that will be the number of
        registrations linked to this line. This method update existing registrations
        and create new one for missing one. """
        Registration = self.env["event.registration"].sudo()
        registrations = Registration.search([("sale_order_line_id", "in", self.ids)])
        for so_line in self.filtered("event_id"):
            existing_registrations = registrations.filtered(
                lambda self: self.sale_order_line_id.id == so_line.id
            )
            if confirm:
                existing_registrations.filtered(
                    lambda self: self.state not in ["open", "cancel"]
                ).confirm_registration()
            if cancel_to_draft:
                existing_registrations.filtered(
                    lambda self: self.state == "cancel"
                ).do_draft()

            for count in range(
                int(so_line.product_uom_qty) - len(existing_registrations)
            ):
                registration = {}
                if registration_data:
                    registration = registration_data.pop()
                # TDE CHECK: auto confirmation
                registration["sale_order_line_id"] = so_line
                Registration.create(Registration._prepare_attendee_values(registration))
        return True

    # 7. Action methods

    # 8. Business methods
