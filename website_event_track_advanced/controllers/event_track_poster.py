# -*- coding: utf-8 -*-

from operator import attrgetter
from odoo import http, fields
from odoo.http import request

from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController
from odoo.tools import html2plaintext


class WebsiteEventTrackController(WebsiteEventTrackController):

    # Single poster
    @http.route(
        ['''/event/<model("event.event"):event>/poster/<model("event.track","[('event_id','=',event[0])]"):track>'''],
        type='http',
        auth='public',
        website=True
    )
    def event_track_poster_view(self, event, track, **post):
        track = track.sudo()
        values = {
            'track': track,
            'event': track.event_id,
            'main_object': track
        }
        return request.render(
            'website_event_track_advanced.poster_view',
            values
        )

    # Poster listing
    @http.route([
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/poster''',
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/poster/tag/<model("event.track.tag"):tag>'''
        ], type='http', auth="public", website=True)
    def event_track_poster(self, event, tag=None, **post):
        searches = {}

        posters = request.env['event.track'].with_context(
            tz=event.date_tz).search([
            ('type.code', '=', 'poster'),
            ('website_published', '=', True),
        ])
        posters = posters.sorted(key=attrgetter('date', 'name'))

        if tag:
            searches.update(tag=tag.id)
            tracks = posters.filtered(lambda track: tag in track.tag_ids)
        else:
            tracks = posters

        values = {
            'event': event,
            'main_object': event,
            'tracks': tracks,
            'tags': event.tracks_tag_ids,
            'tag_id': tag,
            'searches': searches,
            'html2plaintext': html2plaintext
        }
        return request.render("website_event_track_advanced.poster_list",
                              values)