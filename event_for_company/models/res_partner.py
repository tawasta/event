##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2024- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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

# 3. Odoo imports (openerp):
from odoo import _, fields, models

# 2. Known third party imports:

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ResPartner(models.Model):

    # 1. Private attributes
    _inherit = "res.partner"

    # 2. Fields declaration
    company_event_ids = fields.One2many(
        comodel_name="event.event",
        inverse_name="for_company_id",
        string="Company events",
        help="Events for this company",
    )
    company_event_ids_count = fields.Integer(
        string="Company events count",
        compute="_compute_company_events_count",
        readonly=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_company_events_count(self):
        for rec in self:
            rec.company_event_ids_count = len(rec.company_event_ids)

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def action_view_company_events(self):
        """Show company's events"""
        self.ensure_one()
        event_ids = self.with_context(active_test=False).company_event_ids.ids
        domain = [("id", "in", event_ids)]
        return {
            "name": _("Company events"),
            "domain": domain,
            "res_model": "event.event",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "tree,form",
            "view_type": "form",
            "limit": 80,
        }

    # 8. Business methods
