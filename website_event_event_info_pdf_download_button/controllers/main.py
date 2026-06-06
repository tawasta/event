from werkzeug.exceptions import NotFound

from odoo import _, http
from odoo.http import request


class WebsiteEventInfoPdf(http.Controller):
    @http.route(
        ['/event/<model("event.event"):event>/download-info-pdf'],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def download_event_info_pdf(self, event, **kwargs):
        # Create and download the event info PDF

        if not event.can_access_from_current_website():
            raise NotFound()

        is_editor = request.env.user.has_group("website.group_website_designer")
        if not is_editor and not event.sudo().is_published:
            raise NotFound()

        report_ref = (
            "website_event_event_info_pdf_download_button.action_report_event_info"
        )
        pdf_content, _content_type = (
            request.env["ir.actions.report"]
            .sudo()
            ._render_qweb_pdf(report_ref, res_ids=[event.id])
        )

        filename = _("Event_info.pdf")

        headers = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf_content)),
            ("Content-Disposition", 'attachment; filename="%s"' % filename),
        ]
        return request.make_response(pdf_content, headers=headers)
