from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        comodel_name="event.track.rating.grade", string="Track Grade"
    )
    comment = fields.Html("Comment")

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_event_id(self):
        for rating in self:
            if rating.event_track:
                rating.event_id = rating.event_track.event_id
            else:
                rating.event_id = False

    # 5. Constraints and onchanges
    @api.constrains("reviewer_id")
    def _ensure_no_duplicate_rating(self):
        for rec in self:
            existing_rating = self.env["event.track.rating"].search(
                [
                    ["reviewer_id", "=", rec.reviewer_id.id],
                    ["event_track", "=", rec.event_track.id],
                    ["id", "!=", rec.id],
                ]
            )
            if existing_rating:
                raise ValidationError(
                    _(
                        "Rating for track %s by reviewer %s already exists."
                        % (rec.event_track.name, rec.reviewer_id.name)
                    )
                )

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class TrackRatingGrade(models.Model):
    # 1. Private attributes
    _name = "event.track.rating.grade"
    _description = "Event Track Rating Grade"
    _order = "name, grade"

    # 2. Fields declaration
    name = fields.Char(string="Name", required=True, translate=True)
    grade = fields.Integer(string="Grade", required=True)

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
