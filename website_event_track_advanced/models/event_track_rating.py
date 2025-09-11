from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TrackRating(models.Model):
    _name = "event.track.rating"
    _description = "Event Track Rating"
    _order = "event_track, grade_id"
    _rec_name = "grade_id"

    active = fields.Boolean(default=True)
    event_id = fields.Many2one(
        "event.event", "Event", compute="_compute_event_id", readonly=True
    )
    event_track = fields.Many2one("event.track", required=True)
    reviewer_id = fields.Many2one("event.track.reviewer", "Reviewer", required=True)
    grade_id = fields.Many2one(
        comodel_name="event.track.rating.grade", string="Track Grade"
    )
    comment = fields.Html()

    def _compute_event_id(self):
        for rating in self:
            if rating.event_track:
                rating.event_id = rating.event_track.event_id
            else:
                rating.event_id = False

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
                        "Rating for track %(track)s by reviewer %(reviewer)s "
                        "already exists."
                    )
                    % {
                        "track": rec.event_track.name,
                        "reviewer": rec.reviewer_id.name,
                    }
                )


class TrackRatingGrade(models.Model):
    _name = "event.track.rating.grade"
    _description = "Event Track Rating Grade"
    _order = "name, grade"

    name = fields.Char(required=True, translate=True)
    grade = fields.Integer(required=True)
