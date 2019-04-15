# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    event_introduction_track_id = fields.Many2one(
        comodel_name='event.track',
        string='Event introduction',
        help='Use this presentation as event introduction',
    )
