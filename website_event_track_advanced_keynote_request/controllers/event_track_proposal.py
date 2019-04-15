# -*- coding: utf-8 -*-

# 1. Standard library imports:
import logging

# 2. Known third party imports:

# 3. Odoo imports (openerp):

# 4. Imports from Odoo modules:
from odoo.addons.website_event_track_advanced.controllers.event_track_proposal import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:
_logger = logging.getLogger(__name__)


class WebsiteEventTrackController(WebsiteEventTrackController):

    def _get_event_track_proposal_post_values(self, event, **post):
        values = super(WebsiteEventTrackController, self)._get_event_track_proposal_post_values(event, **post)

        values['track']['keynote_speaker_request'] = post.get('keynote_speaker_request')

        return values

