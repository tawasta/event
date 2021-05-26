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
from odoo import fields, models, api
from odoo.osv import expression

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):

    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_is_participating(self):
        """Heuristic
          * public, no visitor: not participating as we have no information;
          * public and visitor: check visitor is linked to a registration. As
            visitors are merged on the top parent, current visitor check is
            sufficient even for successive visits;
          * logged, no visitor: check partner is linked to a registration. Do
            not check the email as it is not really secure;
          * logged as visitor: check partner or visitor are linked to a
            registration;
        """
        current_visitor = self.env["website.visitor"]._get_visitor_from_request(
            force_create=False
        )
        if self.env.user._is_public() and not current_visitor:
            events = self.env["event.event"]
        elif self.env.user._is_public():
            events = (
                self.env["event.registration"]
                .sudo()
                .search(
                    [
                        ("event_id", "in", self.ids),
                        ("state", "!=", "cancel"),
                        ("state", "!=", "wait"),
                        ("visitor_id", "=", current_visitor.id),
                    ]
                )
                .event_id
            )
        else:
            if current_visitor:
                domain = [
                    "|",
                    ("partner_id", "=", self.env.user.partner_id.id),
                    ("visitor_id", "=", current_visitor.id),
                ]
            else:
                domain = [("partner_id", "=", self.env.user.partner_id.id)]
            events = (
                self.env["event.registration"]
                .sudo()
                .search(
                    expression.AND(
                        [
                            domain,
                            [
                                "&",
                                ("event_id", "in", self.ids),
                                ("state", "!=", "cancel"),
                                ("state", "!=", "wait"),
                            ],
                        ]
                    )
                )
                .event_id
            )

        for event in self:
            event.is_participating = event in events

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
