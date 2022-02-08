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
from odoo import _, api, fields, models

# 4. Imports from Odoo modules:
from odoo.exceptions import ValidationError

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackReviewer(models.Model):
    # 1. Private attributes
    _name = "event.track.reviewer"
    _description = "Event Track Reviewer"
    _order = "user_id"
    _rec_name = "user_id"

    # 2. Fields declaration
    user_id = fields.Many2one("res.users", string="User", store=True, required=True)
    review_group_ids = fields.Many2many(
        comodel_name="event.track.review.group", string="Review groups"
    )
    ratings_todo_count = fields.Integer(
        string="Ratings to do", compute="_compute_ratings_todo_count"
    )
    ratings_done_count = fields.Integer(
        string="Ratings done", compute="_compute_ratings_done_count"
    )
    ratings_done_percent = fields.Float(
        string="Rated %", compute="_compute_ratings_done_percent", group_operator="avg"
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_ratings_todo_count(self):
        for record in self:
            record.ratings_todo_count = self.env["event.track"].search_count(
                [("message_partner_ids", "=", record.id)]
            )

    def _compute_ratings_done_count(self):
        for record in self:
            if record.user_id:
                record.ratings_done_count = self.env["event.track.rating"].search_count(
                    [("reviewer_id", "=", record.user_id.id)]
                )

    def _compute_ratings_done_percent(self):
        for record in self:
            if record.ratings_todo_count:
                record.ratings_done_percent = (
                    float(record.ratings_done_count)
                    / float(record.ratings_todo_count)
                    * 100
                )
            else:
                record.ratings_done_percent = 100

    # 5. Constraints and onchanges
    @api.constrains("user_id")
    def _ensure_no_duplicate_user(self):
        for record in self:
            existing_reviewer = self.env["event.track.reviewer"].search(
                [["user_id", "=", record.user_id.id], ["id", "!=", record.id]]
            )
            if existing_reviewer:
                raise ValidationError(
                    _("Reviewer for user %s already exists.", record.user_id.name)
                )

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
