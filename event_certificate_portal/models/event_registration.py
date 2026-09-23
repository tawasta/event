import base64

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class EventRegistration(models.Model):
    _inherit = "event.registration"

    certificate_sent = fields.Boolean(
        string="Certificate sent",
        copy=False,
        readonly=True,
        tracking=True,
    )
    certificate_sent_date = fields.Datetime(
        string="Certificate sent at",
        copy=False,
        readonly=True,
    )

    def _get_certificate_holder_partners(self):
        self.ensure_one()
        partners = self.env["res.partner"]

        if self.partner_id:
            partners |= self.partner_id.commercial_partner_id

        if self.visitor_id and self.visitor_id.partner_id:
            partners |= self.visitor_id.partner_id.commercial_partner_id

        return partners

    def _portal_can_access_certificate(self, user=None):
        self.ensure_one()
        user = user or self.env.user

        if not user or user._is_public():
            return False

        return (
            user.partner_id.commercial_partner_id
            in self._get_certificate_holder_partners()
        )

    def _check_certificate_access(self, user=None):
        self.ensure_one()

        if not self.event_id.certificate_enabled:
            raise AccessError(_("Certificate is not enabled for this event."))

        if self.state != "done":
            raise AccessError(
                _("Certificate is only available for attended registrations.")
            )

        if not self._portal_can_access_certificate(user=user):
            raise AccessError(_("You do not have access to this certificate."))

    def _get_certificate_report_filename(self):
        self.ensure_one()
        holder_name = (
            self.name
            or self.partner_id.name
            or (
                self.visitor_id.partner_id.name
                if self.visitor_id and self.visitor_id.partner_id
                else ""
            )
            or "certificate"
        )
        return ("Osallistumistodistus - %s.pdf" % holder_name).replace("/", "-")

    def _build_certificate_portal_url(self):
        self.ensure_one()
        return "/my/events/registration/%s/certificate" % self.id

    def _get_certificate_email_to(self):
        self.ensure_one()

        if self.email:
            return self.email
        if self.partner_id and self.partner_id.email:
            return self.partner_id.email
        if (
            self.visitor_id
            and self.visitor_id.partner_id
            and self.visitor_id.partner_id.email
        ):
            return self.visitor_id.partner_id.email
        return False

    def action_print_certificate(self):
        self.ensure_one()
        lang = self.event_id.certificate_lang or self.env.lang
        return (
            self.env.ref("event_certificate_portal.action_report_event_certificate")
            .with_context(lang=lang)
            .report_action(self)
        )

    def _render_certificate_pdf(self):
        self.ensure_one()
        report_action = self.env.ref(
            "event_certificate_portal.action_report_event_certificate",
            raise_if_not_found=False,
        )
        if not report_action:
            return b""

        lang = self.event_id.certificate_lang or self.env.lang

        pdf_content, _content_type = (
            self.env["ir.actions.report"]
            .sudo()
            .with_context(lang=lang)
            ._render_qweb_pdf(
                report_action.report_name,
                [self.id],
            )
        )
        return pdf_content

    def _create_certificate_attachment(self):
        self.ensure_one()

        pdf_content = self._render_certificate_pdf()
        if not pdf_content:
            return self.env["ir.attachment"]

        return (
            self.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "name": self._get_certificate_report_filename(),
                    "type": "binary",
                    "datas": base64.b64encode(pdf_content),
                    "mimetype": "application/pdf",
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )
        )

    def _send_certificate_email(self):
        template = self.env.ref(
            "event_certificate_portal.email_template_event_certificate",
            raise_if_not_found=False,
        )
        if not template:
            return

        for registration in self:
            if registration.certificate_sent:
                continue
            if not registration.event_id.certificate_enabled:
                continue
            if not registration.event_id.certificate_send_email:
                continue
            if registration.state != "done":
                continue
            if not registration.event_id.is_finished:
                continue

            email_to = registration._get_certificate_email_to()
            if not email_to:
                continue

            attachment = registration._create_certificate_attachment()
            email_values = {
                "email_to": email_to,
            }
            if attachment:
                email_values["attachment_ids"] = [(4, attachment.id)]

            template.send_mail(
                registration.id,
                force_send=True,
                email_values=email_values,
            )

            registration.write(
                {
                    "certificate_sent": True,
                    "certificate_sent_date": fields.Datetime.now(),
                }
            )

    @api.model
    def cron_send_event_certificates(self):
        registrations = self.search(
            [
                ("state", "=", "done"),
                ("certificate_sent", "=", False),
                ("event_id.certificate_enabled", "=", True),
                ("event_id.certificate_send_email", "=", True),
                ("event_id.is_finished", "=", True),
            ]
        )
        registrations._send_certificate_email()
