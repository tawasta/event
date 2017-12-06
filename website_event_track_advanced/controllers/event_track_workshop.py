# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request

from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController
from odoo.tools import html2plaintext

class WebsiteEventTrackController(WebsiteEventTrackController):

    @http.route([
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/workshop''',
        '''/event/<model("event.event", "[('show_tracks','=',1)]"):event>/workshop/tag/<model("event.track.tag"):tag>'''
        ], type='http', auth="public", website=True)
    def event_track_workshop(self, event, tag=None, **post):
        searches = {}
        workshops = request.env['event.track'].search([
            ('type.code', '=', 'workshop'),
            ('state', '=', 'published'),
        ])

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
            'searches': searches,
            'html2plaintext': html2plaintext
        }
        return request.render("website_event_track_advanced.workshop_list", values)