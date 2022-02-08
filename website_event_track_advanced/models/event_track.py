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


class EventTrack(models.Model):
    # 1. Private attributes
    _inherit = "event.track"

    # 2. Fields declaration
    ratings = fields.One2many("event.track.rating", "event_track_id", string="Ratings")
    ratings_count = fields.Integer("Ratings Count", compute="_compute_ratings_count")
    rating_avg = fields.Float(
        "Average rating",
        digits=(3, 2),
        compute="_compute_rating_avg",
        store=True,
        copy=False,
    )
    grade_id = fields.Many2one(
        "event.track.rating.grade",
        index=True,
        store=False,
        string="Rating",
        compute="_compute_user_rating",
        inverse="_inverse_user_rating",
    )
    rating_comment = fields.Char(
        string="Verbal Rating",
        store=False,
        compute="_compute_user_rating",
        inverse="_inverse_user_rating",
    )
    review_group = fields.Many2one(
        comodel_name="event.track.review.group", string="Review Group"
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_ratings_count(self):
        for rec in self:
            rec.ratings_count = len(rec.ratings)

    def _compute_rating_avg(self):
        for rec in self:
            if not rec.ratings:
                continue
            ratings_sum = 0
            for rating in rec.ratings:
                ratings_sum += rating.grade_id.grade
            rec.rating_avg = float(ratings_sum) / float(rec.ratings_count)

    def _compute_user_rating(self):
        for rec in self:
            print("###################")
            print("###################")
            print("###################")
            all_rev = self.env["event.track.reviewer"].search([])
            print(all_rev)
            reviewer = self.env["event.track.reviewer"].search(
                [("user_id", "=", rec.env.user.id)]
            )
            if reviewer:
                existing_rating = rec.ratings.search(
                    [("reviewer_id", "=", reviewer.id), ("event_track_id", "=", rec.id)]
                )
                if existing_rating:
                    rec.grade_id = existing_rating.grade_id
                    rec.rating_comment = existing_rating.comment

    def _inverse_user_rating(self):
        for rec in self:
            reviewer = self.env["event.track.reviewer"].search(
                [("user_id", "=", rec.env.user.id)]
            )
            if not reviewer:
                reviewer = self.env["event.track.reviewer"].create(
                    {"user_id": rec.env.user.id}
                )
            print("@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@")
            print(reviewer)
            existing_rating = rec.ratings.search(
                [("reviewer_id", "=", reviewer.id), ("event_track_id", "=", rec.id)]
            )
            print(existing_rating)
            if existing_rating:
                if rec.grade_id:
                    existing_rating.grade_id = rec.grade_id
                if rec.rating_comment:
                    existing_rating.comment = rec.rating_comment
            else:
                print(rec.grade_id)
                rec.ratings.create(
                    {
                        "event_track_id": rec.id,
                        "reviewer_id": reviewer.id,
                        "grade_id": rec.grade_id.id,
                        "comment": rec.rating_comment,
                    }
                )

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
