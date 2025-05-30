from odoo import models, fields, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class EventMail(models.Model):
    _inherit = "event.mail"

    def _get_event_registration_to_preview(self):
        # Override which record value to prefill with:
        # - if registrations exist for the related event, pick first of those
        # - if not, create a dummy draft registration and pick that

        self.ensure_one()

        if len(self.event_id.registration_ids):
            return self.event_id.registration_ids[0]
        else:
            registration = self.env["event.registration"].create(
                {
                    "event_id": self.event_id.id,
                    "name": "E-mail Preview Example",
                    "email": "preview@example.com",
                    "state": "draft",
                    "placeholder_for_email_preview": True,
                }
            )

            return registration

    def action_launch_email_template_preview(self):
        # Launch the core template preview dialog with prefilled values

        self.ensure_one()

        if self.notification_type != "mail":
            raise ValidationError(_("You can only preview e-mails."))

        event_registration_to_preview = self._get_event_registration_to_preview()

        resource_ref = f"event.registration,{event_registration_to_preview.id}"

        return {
            "type": "ir.actions.act_window",
            "res_model": "mail.template.preview",
            "name": "Preview Email Template",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_mail_template_id": self.template_ref.id,
                "default_resource_ref": resource_ref,
            },
        }
