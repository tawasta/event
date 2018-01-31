# -*- coding: utf-8 -*-

from operator import attrgetter
from odoo import http, fields
from odoo.http import request

from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController
from odoo.tools import html2plaintext


class WebsiteEventTrackController(WebsiteEventTrackController):

    # Single workshop
    @http.route(
        ['''/event/<model("event.event"):event>/workshop/<model("event.track", "[('event_id','=',event[0])]"):track>'''],
        type='http',
        auth='public',
        website=True
    )
    def event_track_workshop_view(self, event, track, **post):
        track = track.sudo()
        values = {
            'track': track,
            'event': track.event_id,
            'main_object': track
        }

        return request.render(
            'website_event_track_advanced.workshop_view',
            values
        )

    # Workshop listing
    @http.route([
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/workshop''',
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/workshop/tag/<model("event.track.tag"):tag>'''
        ], type='http', auth="public", website=True)
    def event_track_workshop(self, event, tag=None, **post):
        searches = {}

        workshops = request.env['event.track'].sudo().with_context(tz=event.date_tz).search([
            ('type.code', '=', 'workshop'),
            ('website_published', '=', True),
        ])
        workshops = workshops.sorted(key=attrgetter('date', 'name'))

        if tag:
            searches.update(tag=tag.id)
            tracks = workshops.filtered(lambda track: tag in track.tag_ids)
        else:
            tracks = workshops

        values = {
            'event': event,
            'main_object': event,
            'tracks': tracks,
            'tags': event.tracks_tag_ids,
            'tag_id': tag,
            'searches': searches,
            'html2plaintext': html2plaintext
        }
        return request.render("website_event_track_advanced.workshop_list", values)