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

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class TrackTag(models.Model):
    # 1. Private attributes
    _inherit = "event.track.tag"

    # 2. Fields declaration
    name = fields.Char(translate=True)
    track_count = fields.Integer(
        string="Track count", compute="_compute_track_count", store=True
    )
    track_count_agenda = fields.Integer(
        string="Track count in agenda",
        compute="_compute_track_count_agenda",
        store=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("track_ids")
    def _compute_track_count(self):
        for record in self:
            record.track_count = len(record.track_ids)

    @api.depends("track_ids")
    def _compute_track_count_agenda(self):
        for record in self:
            published_tracks = (
                record.track_ids.filtered("website_published")
                .filtered("type.show_in_agenda")
                .filtered(lambda t: t.date is not False)
            )
            record.track_count_agenda = len(published_tracks)

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
