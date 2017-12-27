# -*- coding: utf-8 -*-

from odoo import fields, models


class EventTrackLocation(models.Model):
    _inherit = 'event.track.location'
    _order = 'sequence'

    sequence = fields.Integer(
        string='Order',
    )
