# -*- coding: utf-8 -*-

from operator import attrgetter
from odoo import http, fields
from odoo.http import request

from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController
from odoo.tools import html2plaintext


class WebsiteEventTrackController(WebsiteEventTrackController):

    # Presentation listing
    @http.route([
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/presentation''',
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/presentation/tag/<model("event.track.tag"):tag>'''
        ], type='http', auth="public", website=True)
    def event_track_presentation(self, event, tag=None, **post):
        searches = {}

        posters = request.env['event.track'].sudo().with_context(
            tz=event.date_tz).search([
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
        return request.render(
            "website_event_track_advanced.presentation_list",
            values
        )
