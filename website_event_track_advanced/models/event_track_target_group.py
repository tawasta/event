from odoo import fields, models


class EventTrackTargetGroup(models.Model):
    _name = "event.track.target.group"
    _description = "Event Track Target Group"
    _order = "name"

    name = fields.Char(translate=True)
    description = fields.Html(translate=True)
    active = fields.Boolean(default=True)
    event_tracks = fields.One2many(
        comodel_name="event.track", inverse_name="target_group"
    )
