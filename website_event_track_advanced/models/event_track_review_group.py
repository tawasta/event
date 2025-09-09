from odoo import fields, models


class EventTrackReviewGroup(models.Model):
    _name = "event.track.review.group"
    _description = "Event Track Reviewer Group"
    _order = "name"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    reviewers = fields.Many2many(comodel_name="event.track.reviewer")
    event_tracks = fields.One2many(
        comodel_name="event.track", inverse_name="review_group"
    )
