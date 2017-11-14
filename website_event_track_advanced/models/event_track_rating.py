# -*- coding: utf-8 -*-
from odoo import fields, models


class EventTrackRating(models.Model):
    _name = 'event.track.rating'
    _rec_name = 'rating'
    _order = 'event_track, rating'

    event_track = fields.Many2one(
        comodel_name='event.track',
        string='Event track',
    )
    rating = fields.Integer(
        string='Rating',
        group_operator='avg',
    )
    comment = fields.Char(
        string='Comment',
    )
