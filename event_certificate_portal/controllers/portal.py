# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class EventCertificatePortalController(http.Controller):

    @http.route(
        ["/my/events/registration/<int:registration_id>/certificate"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_event_registration_certificate(self, registration_id, **kwargs):
        registration = request.env["event.registration"].sudo().browse(registration_id).exists()
        if not registration:
            return request.not_found()

        try:
            registration._check_certificate_access(user=request.env.user)
        except (AccessError, MissingError):
            return request.not_found()

        report_action = request.env.ref(
            "event_certificate_portal.action_report_event_certificate",
            raise_if_not_found=False,
        )
        if not report_action:
            return request.not_found()

        report_service = request.env["ir.actions.report"].sudo()
        pdf_content, _content_type = report_service._render_qweb_pdf(
            report_action.report_name,
            [registration.id],
        )

        headers = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", str(len(pdf_content))),
            (
                "Content-Disposition",
                'inline; filename="%s"' % registration._get_certificate_report_filename(),
            ),
        ]
        return request.make_response(pdf_content, headers=headers)