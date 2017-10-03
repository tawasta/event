# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError

# 4. Imports from Odoo modules:
from odoo.addons.website_portal_track.controllers.event_track import WebsiteEventTrack
from odoo.addons.website_event_track_request_time.controllers.event_track_proposal import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports


class WebsiteEventTrack(WebsiteEventTrack):

    def _get_event_track_proposal_values(self):
        print "time"
        return super(WebsiteEventTrackController, self)._get_event_track_proposal_values()

    def _get_event_track_proposal_post_values(self, track, **post):
        return WebsiteEventTrackController._get_event_track_proposal_post_values(
            WebsiteEventTrackController(),
            track.event_id,
            **post
        )