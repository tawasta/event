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


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    answer_count = fields.Integer(
        string="Number of Answers",
        store=True,
        readonly=True,
        compute="_compute_answer_count",
    )
    has_answers = fields.Boolean(
        string="Event has answers",
        store=True,
        readonly=True,
        compute="_compute_has_answers",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("registration_ids.registration_answer_ids")
    def _compute_answer_count(self):
        for event in self:
            event.answer_count = len(
                event.mapped("registration_ids.registration_answer_ids")
            )

    @api.depends("answer_count")
    def _compute_has_answers(self):
        for event in self:
            if event.answer_count >= 1:
                event.has_answers = True
            else:
                event.has_answers = False

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
