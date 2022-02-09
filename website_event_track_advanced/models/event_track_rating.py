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
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class TrackRating(models.Model):
    # 1. Private attributes
    _name = "event.track.rating"
    _description = "Event Track Rating"
    _order = "event_track, grade_id"
    _rec_name = "grade_id"

    # 2. Fields declaration
    active = fields.Boolean(default=True)
    event_id = fields.Many2one(
        "event.event", "Event", compute="_compute_event_id", readonly=True
    )
    event_track = fields.Many2one("event.track", "Event Track", required=True)
    reviewer_id = fields.Many2one("event.track.reviewer", "Reviewer", required=True)
    grade_id = fields.Many2one(
        comodel_name="event.track.rating.grade", string="Track grade"
    )
    comment = fields.Char("Comment")

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_event_id(self):
        for rating in self:
            if rating.event_track:
                rating.event_id = rating.event_track.event_id

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class TrackRatingGrade(models.Model):
    # 1. Private attributes
    _name = "event.track.rating.grade"
    _description = "Event Track Rating Grade"
    _rec_name = "grade"

    # 2. Fields declaration
    grade = fields.Integer(string="Grade", required=True)
    code = fields.Char(string="Code")

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
