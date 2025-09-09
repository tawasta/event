import datetime
from itertools import groupby

from odoo import fields, models


class EventTrackLocation(models.Model):
    _inherit = "event.track.location"
    _order = "sequence"

    def _default_sequence(self):
        return (self.search([], order="sequence desc", limit=1).sequence or 0) + 1

    sequence = fields.Integer(default=_default_sequence)
    show_in_agenda = fields.Boolean(help="Show in website agenda", default=True)
    track_ids = fields.One2many(
        comodel_name="event.track", inverse_name="location_id", string="Tracks"
    )
    scheduled_track_ids = fields.One2many(
        comodel_name="event.track",
        inverse_name="location_id",
        string="Scheduled tracks",
        domain=[("date", "!=", False)],
    )

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
