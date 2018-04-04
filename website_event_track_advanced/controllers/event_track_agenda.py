# -*- coding: utf-8 -*-

import collections
import datetime
import pytz
import dateutil.parser
import re
import logging

from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError

from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController
_logger = logging.getLogger(__name__)


class WebsiteEventTrackController(WebsiteEventTrackController):

    # Overwrites the default agenda controller
    @http.route([
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/agenda''',
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/agenda/tag/<model("event.track.tag"):tag>'''
        ],
        type='http',
        auth='public',
        website=True)
    def event_agenda(self, event, tag=None, **post):
        values = self.get_event_agenda_values(event=event, tag=tag, **post)

        return request.render("website_event_track.agenda", values)

    def get_event_agenda_values(self, event, tag=None, **post):
        days_tracks = collections.defaultdict(lambda: [])

        domain_filter = list()
        searches = dict()

        domain_filter.append(('event_id', '=', event.id))
        domain_filter.append(('date', '!=', False))
        domain_filter.append(('website_published', '=', True))
        domain_filter.append(('type.show_in_agenda', '=', True))

        event_tracks = event.track_ids.sudo().search(
            domain_filter,
        )

        # Don't show hidden locations
        event_tracks = event_tracks.filtered(
            lambda track:
            not track.location_id or track.location_id.show_in_agenda
        )

        if tag:
            searches.update(tag=tag.id)
            event_tracks = event_tracks.filtered(lambda track: tag in track.tag_ids)

        for track in event_tracks:
            if not track.date:
                continue
            days_tracks[track.date[:10]].append(track)

        days = dict()
        days_tracks_count = dict()
        for day, tracks in days_tracks.iteritems():
            day_count = 0
            for track in tracks:
                if track.type.attendable:
                    day_count += 1

            days_tracks_count[day] = day_count
            days[day] = self._prepare_calendar(event, tracks)

        speakers = dict()
        tags = dict()

        for track in event_tracks:
            speakers_name = u", ".join(track.speaker_ids.mapped('name'))
            speakers[track.id] = speakers_name

            tag_names = u", ".join(track.tag_ids.mapped('name'))
            tags[track.id] = tag_names

        target_groups = request.env['event.track.target.group'].search([])

        values = {
            'event': event,
            'days': days,
            'days_nbr': days_tracks_count,
            'tag': tag,
            'speakers': speakers,
            'tags': tags,
            'searches': searches,
            'dateparser': dateutil.parser,
            'user': request.env.user,
            'target_groups': target_groups,
        }

        return values

    # Overwrites the default _prepare_calendar
    def _prepare_calendar(self, event, event_track_ids):
        local_tz = pytz.timezone(event.date_tz or 'UTC')
        locations = {}  # { location: [track, start_date, end_date, rowspan]}
        dates = []  # [ (date, {}) ]
        for location in request.env['event.track.location'].search([
            ('show_in_agenda', '=', True),
        ]):
            locations.setdefault(location or False, [])

        forcetr = True
        for track in event_track_ids:
            start_date = fields.Datetime.from_string(track.date).replace(tzinfo=pytz.utc).astimezone(local_tz)
            end_date = start_date + datetime.timedelta(hours=(track.duration or 0.5))
            location = track.location_id or False
            locations.setdefault(location, [])

            # New TR, align all events
            if forcetr or (start_date>dates[-1][0]) or not location:
                dates.append((start_date, {}, bool(location), end_date))
                for loc in locations.keys():
                    if locations[loc] and (locations[loc][-1][2] > start_date):
                        locations[loc][-1][3] += 1
                    elif not locations[loc] or locations[loc][-1][2] <= start_date:
                        locations[loc].append([False, locations[loc] and locations[loc][-1][2] or dates[0][0], start_date, 1])
                        dates[-1][1][loc] = locations[loc][-1]
                forcetr = not bool(location)

            # Add event
            if locations[location] and locations[location][-1][1] > start_date:
                locations[location][-1][3] -= 1
            locations[location].append([track, start_date, end_date, 1])

            dates[-1][1][location] = locations[location][-1]

        # Sort locations
        locations_order = collections.OrderedDict()
        locations_sorted = collections.OrderedDict()

        for key, val in locations.iteritems():
            if key:
                code = key.sequence or key.name

                locations_order[code] = key

        for location in sorted(locations_order):
            location_key = locations_order[location]
            locations_sorted[location_key] = locations.get(location_key, False)

        return {
            'locations': locations_sorted,
            'dates': dates
        }

    @http.route(
        ['/event/track/move'],
        type='json',
        auth='public',
        website=True)
    def event_track_move(self, **post):
        # JSON-route moving tracks

        # Check variables
        old_track_id = post.get('old_track_id', False)
        new_track_id = post.get('new_track_id', False)
        track_model = request.env['event.track']

        try:
            track_model.check_access_rights('read')
            track_model.check_access_rights('write')
        except AccessError:
            _logger.warning('Access error while trying to move a track')
            return 401

        if old_track_id and new_track_id:
            # Strip non numeric characters
            old_track_id = re.sub('[^0-9]', '', old_track_id)
            new_track_id = re.sub('[^0-9]', '', new_track_id)

            old_track = track_model.browse([int(old_track_id)])
            new_track = track_model.browse([int(new_track_id)])

            # Store the variables
            old_location = old_track.location_id
            new_location = new_track.location_id
            old_date = old_track.date
            new_date = new_track.date

            # Swap the values
            old_track.location_id = new_location.id
            new_track.location_id = old_location.id
            old_track.date = new_date
            new_track.date = old_date

            return 200
        else:
            _logger.warning('Unexpected error while trying to move a track')
            return 500
