# -*- coding: utf-8 -*-
import re

from odoo import http, fields
from odoo.http import request

from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController


class WebsiteEventTrackController(WebsiteEventTrackController):

    @http.route(
        ['/event/agenda/program/save'],
        type='json',
        auth='public',
        website=True)
    def event_track_program_save(self, **post):
        # JSON-route for saving program paths
        EventTrackProgramPath = request.env['event.track.program.path']

        # Find an existing program path
        program = EventTrackProgramPath.search([
            ('partner_id', '=', request.uid)
        ], limit=1)

        # Program not found. Create a new
        if not program:
            program = EventTrackProgramPath.create({
                'partner_id': request.uid,
            })

        track_name = post.get('track_id', False)

        if not track_name or 'active' not in post:
            return 500

        track_id = int(re.sub('[^0-9]', '', track_name))

        if post.get('active', False):
            # Remove from program path
            program.track_ids = [(3, track_id, False)]

        else:
            # Add to program path
            program.track_ids = [(4, track_id, False)]

        return 200
