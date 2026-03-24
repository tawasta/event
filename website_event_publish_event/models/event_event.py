##############################################################################
#
#    Author: Futural Oy
#    Copyright 2022- Futural Oy (https://futural.fi)
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

from odoo import models


class EventEvent(models.Model):
    _inherit = "event.event"

    def write(self, vals):
        res = super().write(vals)
        if "website_published" in vals and vals.get("website_published"):
            self.action_set_stage_published()
        return res

    def action_publish_event(self):
        self.website_published = True

    def action_set_stage_published(self):
        first_published_stage = self.env["event.stage"].search(
            [("pipe_publish", "=", True)], order="sequence"
        )
        if first_published_stage:
            self.write({"stage_id": first_published_stage[0].id})
