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
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ResPartner(models.Model):
    # 1. Private attributes
    _inherit = "res.partner"

    # 2. Fields declaration
    event_ids = fields.Many2many(
        "event.event",
        string="Events",
        compute="_compute_event_ids",
        search="_search_event_ids",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_registration_ids")
    def _compute_event_ids(self):
        for partner in self:
            event_ids = self.env["event.event"]
            for registration in partner.event_registration_ids:
                event_ids.append(
                    self.env["event.event"].search(
                        ["registration_ids", "in", registration.id]
                    )
                )
            partner.event_ids = event_ids or False

    def _search_event_ids(self, operator, value):
        domain = [("name", operator, value)]
        event_ids = self.env["event.event"]._search(domain)
        return [("id", "in", event_ids)]

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
