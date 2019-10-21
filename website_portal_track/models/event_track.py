# -*- coding: utf-8 -*-

from odoo import fields, models


class EventTrack(models.Model):
    _inherit = 'event.track'

    event_over = fields.Boolean(
        string='Event over',
        related='event_id.event_over',
    )
