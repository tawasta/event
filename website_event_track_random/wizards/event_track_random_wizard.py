# -*- coding: utf-8 -*-

from odoo import api, fields, models
import random
import dateutil.parser
import datetime


class EventTrackRandomWizard(models.TransientModel):

    _name = 'event.track.random.wizard'

    location = fields.Boolean(
        string='Location',
    )
    date = fields.Boolean(
        string='Date',
    )
    date_start = fields.Datetime(
        string='Start',
    )
    date_end = fields.Datetime(
        string='End',
    )
    break_length = fields.Integer(
        string='Break length (minutes)',
        default=15,
    )

    @api.multi
    def action_track_randomize(self):
        if 'active_ids' not in self._context:
            return False

        self.randomize()

        track_ids = self._context['active_ids']

        return {'active_ids': track_ids}

    def randomize(self):
        track_ids = self._context['active_ids']
        tracks = self.env['event.track'].browse(track_ids)

        if self.location:
            self.randomize_locations(tracks)

        if self.date:
            self.randomize_dates(tracks)

        return True

    def randomize_locations(self, tracks):
        locations = self.env['event.track.location'].search([
            ('use_in_randomization', '=', True)
        ]).ids

        random.shuffle(locations)

        location_iterator = iter(locations)
        keys = range(0, len(tracks) -1)
        random.shuffle(keys)

        for key in keys:
            track = tracks[key]

            if track.location_id:
                continue

            try:
                next = location_iterator.next()
            except StopIteration:
                location_iterator = iter(locations)
                next = location_iterator.next()

            track.location_id = next

        return True

    def randomize_dates(self, tracks):
        locations = self.env['event.track.location'].search([])

        # Loop through tracks by location
        for location in locations:
            date_start = dateutil.parser.parse(self.date_start)
            date_end = dateutil.parser.parse(self.date_end)

            current_tracks = tracks.filtered(
                lambda r: r.location_id.id == location.id
            )

            keys = range(0, len(current_tracks))
            random.shuffle(keys)

            for key in keys:
                track = current_tracks[key]

                if track.date:
                    continue

                new_date = date_start.replace(microsecond=0)\
                    .isoformat().replace('T', ' ')
                date_start = date_start + datetime.timedelta(
                    minutes=track.duration*60 + self.break_length
                )

                if date_start > date_end:
                    continue

                track.date = new_date

        return True