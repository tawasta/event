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
import datetime

# 2. Known third party imports:
from itertools import groupby

# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class TrackLocation(models.Model):
    # 1. Private attributes
    _inherit = "event.track.location"
    _order = "sequence"

    def _default_sequence(self):
        return (self.search([], order="sequence desc", limit=1).sequence or 0) + 1

    # 2. Fields declaration
    sequence = fields.Integer(string="Sequence", default=_default_sequence)
    show_in_agenda = fields.Boolean(
        string="Show in agenda", help="Show in website agenda", default=True
    )
    track_ids = fields.One2many(
        comodel_name="event.track", inverse_name="location_id", string="Tracks"
    )
    scheduled_track_ids = fields.One2many(
        comodel_name="event.track",
        inverse_name="location_id",
        string="Scheduled tracks",
        domain=[("date", "!=", False)],
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    def get_grouped_tracks(self):
        """Group tracks based on date and return a grouped list to use in reports"""
        tracks = self.scheduled_track_ids.filtered(
            lambda track: track.date.date() >= datetime.date.today()
            and track.type.attendable
        ).sorted(key=lambda t: t.date.date())
        grouped_tracks = [
            list(j) for _i, j in groupby(tracks, key=lambda t: t.date.date())
        ]
        return grouped_tracks
