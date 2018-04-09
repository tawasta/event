# -*- coding: utf-8 -*-

from odoo import fields, models


class EventTrackLocation(models.Model):
    _inherit = 'event.track.location'
    _order = 'sequence'

    sequence = fields.Integer(
        string='Order',
    )

    show_in_agenda = fields.Boolean(
        string='Show in agenda',
        help='Show in website agenda',
        default=True,
    )

    track_ids = fields.One2many(
        comodel_name='event.track',
        inverse_name='location_id',
        string='Tracks',
    )
