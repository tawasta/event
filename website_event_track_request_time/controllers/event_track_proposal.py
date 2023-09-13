# 1. Standard library imports:
import logging

# 3. Odoo imports:
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.website_event_track_advanced.controllers.event_track import (
    EventTrackControllerAdvanced,
)

# 2. Known third party imports:


# from odoo.addons.website_event_track.controllers.\
# main import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:
_logger = logging.getLogger(__name__)


class RequestEventTrackController(EventTrackControllerAdvanced):
    def _get_event_track_proposal_form_values(self, event, **post):
        values = super(
            RequestEventTrackController, self
        )._get_event_track_proposal_form_values(event, **post)
        values["request_times"] = (
            request.env["event.track.request.time"].sudo().search([])
        )
        return values

    def _get_event_track_proposal_post_values(self, event, **post):
        values = super(
            RequestEventTrackController, self
        )._get_event_track_proposal_post_values(event, **post)

        if post.get("request_time") and post.get("request_time") != "false":
            values["track"]["request_time"] = post.get("request_time")

        return values
