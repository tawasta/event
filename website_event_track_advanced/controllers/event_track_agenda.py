# -*- coding: utf-8 -*-

import collections
import datetime
import pytz
import dateutil.parser

from odoo import http, fields
from odoo.http import request

from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController


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

        return request.render("website_event_track.agenda", {
            'event': event,
            'days': days,
            'days_nbr': days_tracks_count,
            'speakers': speakers,
            'tag': tag,
            'searches': searches,
            'dateparser': dateutil.parser,
        })

    # Overwrites the default _prepare_calendar
    def _prepare_calendar(self, event, event_track_ids):
        local_tz = pytz.timezone(event.date_tz or 'UTC')
        locations = {}                  # { location: [track, start_date, end_date, rowspan]}
        dates = []                      # [ (date, {}) ]
        for track in event_track_ids:
            locations.setdefault(track.location_id or False, [])

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
                locations_order[key.sequence] = key

        for location in sorted(locations_order):
            location_key = locations_order[location]
            locations_sorted[location_key] = locations.get(location_key, False)

        return {
            'locations': locations_sorted,
            'dates': dates
        }