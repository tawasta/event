import logging

from odoo import SUPERUSER_ID, _, http
from odoo.exceptions import UserError
from odoo.http import content_disposition, request

_logger = logging.getLogger(__name__)


class WebsiteEventControllerDownloadBadge(http.Controller):
    @http.route(
        ['/event/<model("event.event"):event>/registration/badge/<string:code>'],
        type="http",
        auth="public",
        website=True,
    )
    def download_reg_badge(self, event, code, **post):
        """
        Return registration badge download page and
        save privacy values on post
        """
        for registration in event.sudo().registration_ids:
            if registration.sudo().access_token == code:
                render_values = {
                    "event": event,
                    "registration": registration,
                    "ticket": registration.event_ticket_id,
                    "privacies": event.sudo().privacy_ids,
                }
                if post:
                    self._create_privacy(
                        post, registration, registration.partner_id, event
                    )
                    try:
                        registration.sudo().write(
                            {"registration_badge_downloaded": True}
                        )
                    except ValueError:
                        _logger.error(
                            _(
                                "Could not set registration '{}' badge as downloaded".format(
                                    registration.id
                                )
                            )
                        )



                    pdf = \
                    request.env['ir.actions.report'].sudo()._render_qweb_pdf('event.event_registration_report_template_badge', [registration.id])[0]

                    pdfhttpheaders = [
                        ("Content-Type", "application/pdf"),
                        ("Content-Length", len(pdf)),
                        (
                            "Content-Disposition",
                            'attachment; filename="%s.pdf"' % registration.partner_id.name,
                        ),
                    ]
                    return request.make_response(pdf, headers=pdfhttpheaders)

                return request.render(
                    "website_event_download_registration_badge.download_badge_page",
                    render_values,
                )
        return request.render("website.page_404")

    def _create_privacy(self, post, registration, partner, event):
        """Create privacies"""
        privacy_ids = []
        for privacy in event.privacy_ids:
            if post.get("privacy_" + str(privacy.id)):
                privacy_ids.append(privacy.id)

        if privacy_ids:
            for pr in event.privacy_ids:
                accepted = pr.id in privacy_ids
                privacy_values = {
                    "partner_id": partner.id,
                    "registration_ids": [(4, registration.id, 0)],
                    "activity_id": pr.id,
                    "accepted": accepted,
                    "state": "answered",
                }
                already_privacy_record = (
                    request.env["privacy.consent"]
                    .sudo()
                    .search(
                        [("partner_id", "=", partner.id), ("activity_id", "=", pr.id)]
                    )
                )
                if already_privacy_record:
                    already_privacy_record.sudo().write(
                        {
                            "accepted": accepted,
                            "registration_ids": [(4, registration.id, 0)],
                        }
                    )
                else:
                    request.env["privacy.consent"].sudo().create(privacy_values)


