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


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def action_set_in_progress(self):
        """
        Action which will move the events
        into the first next (by sequence) stage defined as "In Progress"
        (if they are not already in an in progress stage)
        """
        first_in_progress_stage = self.env["event.stage"].search(
            [("pipe_in_progress", "=", True)], order="sequence"
        )
        if first_in_progress_stage:
            self.write({"stage_id": first_in_progress_stage[0].id})

    # 8. Business methods
    @api.autovacuum
    def _gc_mark_events_in_progress(self):
        """move every in progress events in the next 'in progress stage'"""
        in_progress_events = self.env["event.event"].search(
            [
                ("date_begin", "<", fields.Datetime.now()),
                ("date_end", ">", fields.Datetime.now()),
                ("stage_id.pipe_in_progress", "=", False),
            ]
        )
        if in_progress_events:
            in_progress_events.action_set_in_progress()
