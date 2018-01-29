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

        program = EventTrackProgramPath.sudo().search([
            ('partner_id', '=', request.uid)
        ], limit=1)

        if program:
            res['program_track_ids'] = program.track_ids

        return res
