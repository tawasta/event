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
                    return self._show_report(
                        model=registration,
                        report_type="pdf",
                        report_ref="event.report_event_registration_badge",
                        download=True,
                    )

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

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ("html", "pdf", "text"):
            raise UserError(_("Invalid report type: %s", report_type))

        report_sudo = request.env.ref(report_ref).with_user(SUPERUSER_ID)

        if not isinstance(report_sudo, type(request.env["ir.actions.report"])):
            raise UserError(_("%s is not the reference of a report", report_ref))

        if hasattr(model, "company_id"):
            report_sudo = report_sudo.with_company(model.company_id)

        method_name = "_render_qweb_%s" % (report_type)
        report = getattr(report_sudo, method_name)(
            [model.id], data={"report_type": report_type}
        )[0]
        reporthttpheaders = [
            (
                "Content-Type",
                "application/pdf" if report_type == "pdf" else "text/html",
            ),
            ("Content-Length", len(report)),
        ]
        if report_type == "pdf" and download:
            filename = "Registration Badge - %s.pdf" % model.name
            reporthttpheaders.append(
                ("Content-Disposition", content_disposition(filename))
            )
        return request.make_response(report, headers=reporthttpheaders)
