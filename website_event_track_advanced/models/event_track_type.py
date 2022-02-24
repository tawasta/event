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
import re

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackType(models.Model):
    # 1. Private attributes
    _name = "event.track.type"
    _description = "Event Track Type"
    _order = "sequence, name"

    def _default_sequence(self):
        return (self.search([], order="sequence desc", limit=1).sequence or 0) + 1

    # 2. Fields declaration
    sequence = fields.Integer(string="Sequence", default=_default_sequence)
    code = fields.Char(copy=False, translate=False, required=True)
    name = fields.Char(translate=True, required=True)
    description = fields.Text(translate=True)
    active = fields.Boolean(default=True)
    event_tracks = fields.One2many(
        comodel_name="event.track", inverse_name="type", string="Event Track"
    )
    show_in_proposals = fields.Boolean(
        string="Show in proposals", help="Show in proposals form", default=True
    )
    show_in_agenda = fields.Boolean(
        string="Show in agenda", help="Show in website agenda", default=True
    )
    attendable = fields.Boolean(
        string="Attendable",
        help="If the presentation type can be attended. "
        "Unattendable types will be muted in the agenda",
        default=True,
    )
    twitter_hashtag = fields.Char(
        string="Twitter hashtag", help="Twitter hashtag for tracks"
    )
    workshop = fields.Boolean(
        string="Workshop", help="Tracks in this Type can hold workshops", default=False
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    _sql_constraints = [("code", "unique(code)", "Please use an unique code")]

    @api.onchange("twitter_hashtag")
    def onchange_twitter_hashtag_sanitize(self):
        for record in self:
            if record.twitter_hashtag:
                hashtag = re.sub("[^A-Za-z0-9_]", "", record.twitter_hashtag)
                record.twitter_hashtag = hashtag

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
