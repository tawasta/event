# -*- coding: utf-8 -*-
from odoo import fields, models


class EventTrackLocation(models.Model):
    _inherit = 'event.track.location'

    use_in_randomization = fields.Boolean(
        string='Use in randomization',
        default=True,
    )
