# -*- coding: utf-8 -*-
from odoo import fields, models, api


class EventTrackRating(models.Model):
    _name = 'event.track.rating'
    _rec_name = 'rating'
    _order = 'event_track, rating'

    active = fields.Boolean(
        default=True,
    )

    event_id = fields.Many2one(
        comodel_name='event.event',
        string='Event',
        related='event_track.event_id',
    )
    event_track = fields.Many2one(
        comodel_name='event.track',
        string='Presentation',
    )
    rating = fields.Integer(
        string='Rating',
        group_operator='avg',
    )
    comment = fields.Char(
        string='Comment',
    )

    @api.depends('active')
    def _compute_track_rating(self):
        for record in self:
            record.event_track._compute_rating_avg()
