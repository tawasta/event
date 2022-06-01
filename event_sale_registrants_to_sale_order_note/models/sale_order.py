##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
from odoo import _, models

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

    # 7. Action methods
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for so in self:
            registrations = (
                self.env["event.registration"]
                .sudo()
                .search([("sale_order_id", "in", so.ids), ("state", "!=", "cancel")])
            )
            if registrations:
                registration_names = []
                for registration in registrations:
                    registration_names.append(registration.name)
                registrations_note = _("Linked Registrations: %s") % ",".join(
                    registration_names
                )
                if so.note:
                    new_note = so.note + "\n" + registrations_note
                else:
                    new_note = registrations_note
                so.sudo().write({"note": new_note})
        return res

    # 8. Business methods
