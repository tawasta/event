from odoo import http
from odoo.http import request

from odoo.addons.website_event_track_advanced.controllers.event_track import EventTrackControllerAdvanced


class EventTrackControllerAdvancedPrivacy(EventTrackControllerAdvanced):
    @http.route()
    def event_track_proposal_post(self, event, **post):
        response_data = super(EventTrackControllerAdvancedPrivacy, self).event_track_proposal_post(event, **post)
        current_track = response_data.qcontext['track']
        self._create_privacy(post, current_track.partner_id, current_track.event_id)

        return response_data

    def _create_privacy(self, post, partner, event):
        """ Create privacies """
        privacy_ids = []
        for privacy in event.privacy_ids:
            if post.get("privacy_" + str(privacy.id)):
                privacy_ids.append(privacy.id)

        if privacy_ids:
            for pr in event.privacy_ids:
                accepted = pr.id in privacy_ids
                privacy_values = {
                    "partner_id": partner.id,
                    "activity_id": pr.id,
                    "accepted": accepted,
                    "state": "answered",
                }
                already_privacy_record = (
                    request.env["privacy.consent"]
                    .sudo()
                    .search(
                        [
                            ("partner_id", "=", partner.id,),
                            ("activity_id", "=", pr.id),
                        ]
                    )
                )
                if already_privacy_record:
                    already_privacy_record.sudo().write({"accepted": accepted})
                else:
                    request.env["privacy.consent"].sudo().create(privacy_values)
