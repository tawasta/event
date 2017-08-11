# -*- coding: utf-8 -*-

# 1. Standard library imports:
import collections

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, fields
from odoo.http import request

# 4. Imports from Odoo modules (rarely, and only if necessary):
from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in


class WebsiteEventTrackController(WebsiteEventTrackController):

    @http.route()
    def event_agenda(self, event, tag=None, **post):
        days_tracks = collections.defaultdict(lambda: [])

        # TODO: fix the security rule
        tracks = request.env['event.track'].sudo().search([('event_id', '=', event.id)])
        print tracks
        for track in tracks.sorted(lambda track: (track.date, bool(track.location_id))):
            if not track.date:
                continue
            days_tracks[track.date[:10]].append(track)

        days = {}
        days_tracks_count = {}
        for day, tracks in days_tracks.iteritems():
            days_tracks_count[day] = len(tracks)
            days[day] = self._prepare_calendar(event, tracks)

        speakers = {}
        for track in event.sudo().track_ids:
            speakers_name = u" – ".join(track.speaker_ids.mapped('name'))
            speakers[track.id] = speakers_name

        return request.render("website_event_track.agenda", {
            'event': event,
            'days': days,
            'days_nbr': days_tracks_count,
            'speakers': speakers,
            'tag': tag
        })
