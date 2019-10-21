# -*- coding: utf-8 -*-

from odoo import fields, models


class EventTrack(models.Model):
    _inherit = 'event.track'

    event_over = fields.Boolean(
        string='Event over',
        related='event_id.event_over',
    )

    event_date_begin = fields.Datetime(
        string='Event start date',
        related='event_id.date_begin',
        store=True,
    )

    event_date_end = fields.Datetime(
        string='Event end date',
        related='event_id.date_end',
        store=True,
    )
