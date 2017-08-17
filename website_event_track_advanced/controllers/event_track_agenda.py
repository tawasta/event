# -*- coding: utf-8 -*-

# 1. Standard library imports:
import collections
import datetime
import pytz

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, fields
from odoo.http import request

# 4. Imports from Odoo modules (rarely, and only if necessary):
from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in


class WebsiteEventTrackController(WebsiteEventTrackController):

    # Overwrites the default agenda controller
    @http.route()
    def event_agenda(self, event, tag=None, **post):
        days_tracks = collections.defaultdict(lambda: [])

        # TODO: fix the security rule
        tracks = request.env['event.track'].sudo().search([('event_id', '=', event.id)])
        for track in tracks.sorted(lambda track: (track.date, bool(track.location_id))):
            if not track.date:
                continue
            days_tracks[track.date[:10]].append(track)

        days = dict()
        days_tracks_count = dict()
        for day, tracks in days_tracks.iteritems():
            days_tracks_count[day] = len(tracks)
            days[day] = self._prepare_calendar(event, tracks)

        speakers = dict()
        tags = dict()
        for track in event.sudo().track_ids:
            speakers_name = u", ".join(track.speaker_ids.mapped('name'))
            speakers[track.id] = speakers_name

            tag_names = u", ".join(track.tag_ids.mapped('name'))
            tags[track.id] = tag_names

        return request.render("website_event_track.agenda", {
            'event': event,
            'days': days,
            'days_nbr': days_tracks_count,
            'speakers': speakers,
            'tags': tags,
            'tag': tag
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
        return {
            'locations': locations,
            'dates': dates
        }