from odoo import http, fields
from odoo.http import request

from odoo.addons.website_event_track_advanced.controllers.event_track_agenda \
    import WebsiteEventTrackController


class WebsiteEventTrackController(WebsiteEventTrackController):

    def get_event_agenda_values(self, event, tag=None, **post):
        res = super(WebsiteEventTrackController, self).get_event_agenda_values(
            event=event,
            tag=tag,
            **post
        )
        EventTrackProgramPath = request.env['event.track.program.path']

        program = EventTrackProgramPath.search([
            ('user_id.id', '=', request.uid)
        ], limit=1)

        user_logged = request.uid != request.website.user_id.id

        if not program and user_logged:
            program = EventTrackProgramPath.create({
                'user_id': request.uid,
            })

        if program:
            res['program'] = program

        res['user_logged'] = user_logged

        return res
