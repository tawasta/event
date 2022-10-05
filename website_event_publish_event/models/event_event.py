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
from odoo import api, models

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
    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        for event in self:
            if event.stage_id.pipe_publish:
                event.action_publish_event()

    @api.onchange("website_published")
    def _onchange_website_published(self):
        for event in self:
            if event.website_published:
                event.action_publish_event()

    # 6. CRUD methods

    # 7. Action methods
    def action_publish_event(self):
        self.website_published = True
        first_published_stage = self.env["event.stage"].search(
            [("pipe_publish", "=", True)], order="sequence"
        )
        if first_published_stage:
            self.write({"stage_id": first_published_stage[0].id})

    # 8. Business methods
