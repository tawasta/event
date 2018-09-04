# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventTrack(models.Model):

    _inherit = 'event.track'

    image_presentation = fields.Binary(
        string='Presentation image',
    )
