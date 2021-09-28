from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class PortalCertificate(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "event_count" in counters:
            values['event_count'] = request.env['event.registration'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id)
            ])

        return values

    @http.route(["/my/events"], type="http", auth="user", website=True)
    def portal_my_events(self, **kw):
        values = self._prepare_portal_layout_values()

        registrations = request.env["event.registration"].search(
            [
                ('partner_id', '=', request.env.user.partner_id.id)
            ]
        )

        values.update(
            {
                "registrations": registrations,
                "page_name": "event",
                "default_url": "/my/events",
            }
        )
        return request.render(
            "website_my_events.portal_my_events", values
        )

    # @http.route(
    #     ["/my/certificates/<int:certificate_id>"],
    #     type="http",
    #     auth="user",
    #     website=True,
    # )
    # def portal_my_certificate_detail(self, certificate_id, **kw):
    #     current_user = request.env.user
    #     is_student = current_user.has_group("society_student_core.group_student")
    #     certificate = request.env["op.batch.students"].search(
    #         [("id", "=", certificate_id)]
    #     )
    #     student = (
    #         request.env["op.student"]
    #         .sudo()
    #         .search([("partner_id", "=", current_user.partner_id.id)], limit=1)
    #     )
    #     if not is_student and certificate.student_id != student:
    #         return request.render("website.page_404")

    #     values = {
    #         "certificate": certificate,
    #         "docs": certificate,
    #         "page_name": "certificate",
    #         "student": student,
    #     }

    #     return request.render(
    #         "website_society_certificate.portal_certificate_page", values
    #     )

    # @http.route(["/certificate/download"], type="http", auth="user", website=True)
    # def certificate_download(self, **post):

    #     pdf, _ = (
    #         request.env.ref("society_certificate.certificate_report_action")
    #         .sudo()
    #         ._render_qweb_pdf([int(post.get("id"))])
    #     )
    #     certificate_id = (
    #         request.env["op.batch.students"]
    #         .sudo()
    #         .search([("id", "=", post.get("id"))])
    #     )

    #     pdfhttpheaders = [
    #         ("Content-Type", "application/pdf"),
    #         ("Content-Length", len(pdf)),
    #         (
    #             "Content-Disposition",
    #             'attachment; filename="%s.pdf"' % certificate_id.student_id.name,
    #         ),
    #     ]
    #     return request.make_response(pdf, headers=pdfhttpheaders)
