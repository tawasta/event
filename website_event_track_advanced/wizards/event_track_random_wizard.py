# -*- coding: utf-8 -*-

from odoo import api, fields, models
import random


class EventTrackRandomWizard(models.TransientModel):

    _name = 'event.track.random.wizard'

    location = fields.Boolean(
        string='Location',
    )
    '''
    date = fields.Boolean(
        string='Location',
    )
    date_start = fields.Datetime(
        string='Start',
    )
    date_end = fields.Datetime(
        string='End',
    )
    '''

    @api.multi
    def action_track_randomize(self):
        if 'active_ids' not in self._context:
            return False

        locations = self.env['event.track.location'].search([])

        track_ids = self._context['active_ids']
        tracks = self.env['event.track'].browse(track_ids)

        for track in tracks:
            if not track.location_id:
                track.location_id = locations[random.randint(0, len(locations)-1)].id

        return {'active_ids': track_ids}
