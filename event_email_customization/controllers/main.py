import json
import logging
import secrets
from datetime import datetime

from odoo import _, http
from odoo.http import request

from odoo.addons.event_ticket_purchase_options.controllers.main import (
    EventRegistrationController,
)

_logger = logging.getLogger(__name__)


class EventEmailCustomizationController(EventRegistrationController):
    @http.route(
        ["/send/invitation"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def send_invitation(self, **post):
        """
        Override to use our custom mail template instead of the original
        event_ticket_purchase_options template. All other logic remains identical.
        """
        registration_id = post.get("registration_id")
        if not registration_id:
            return json.dumps(
                {"status": "error", "message": "Registration ID is missing"}
            )

        registration = (
            request.env["event.registration"]
            .sudo()
            .search([("id", "=", int(registration_id))], limit=1)
        )

        if not registration:
            return json.dumps({"status": "error", "message": "Registration not found"})

        invite_email = post.get("invite_email")
        if not invite_email:
            return json.dumps({"status": "error", "message": "No email provided"})

        if post.get("invite_id"):
            old_invite_id = (
                request.env["registration.invitation"]
                .sudo()
                .search([("id", "=", int(post.get("invite_id")))], limit=1)
            )

            if old_invite_id and old_invite_id == registration.invite_id:
                old_invite_id.unlink()

        invite_tracker = (
            request.env["registration.invitation"]
            .sudo()
            .create(
                {
                    "registration_id": registration.id,
                    "invite_email": invite_email,
                    "invited_date": datetime.now(),
                    "is_used": False,
                    "access_token": secrets.token_urlsafe(32),
                }
            )
        )

        registration.sudo().write({"invite_id": invite_tracker.id})

        # Use our custom template instead of the original
        mail_template = request.env.ref(
            "event_email_customization.event_company_invitation_custom"
        ).sudo()
        if not mail_template:
            return json.dumps(
                {"status": "error", "message": "Email template not found"}
            )

        email_values = {
            "email_to": invite_email,
            "auto_delete": True,
            "message_type": "email",
            "recipient_ids": [],
            "partner_ids": [],
        }

        try:
            mail_template.send_mail(
                registration.id,
                force_send=True,
                raise_exception=True,
                email_values=email_values,
            )
            body = f"An invitation has been sent to the email address: {invite_email}."
            registration.sudo().message_post(
                body=body,
                subject=_("Invitation sent"),
                subtype_xmlid="mail.mt_note",
                message_type="notification",
            )

        except Exception as e:
            return json.dumps(
                {"status": "error", "message": f"Failed to send invitation: {str(e)}"}
            )

        return json.dumps(
            {
                "status": "success",
                "message": _("Invitation sent"),
                "invite_id": invite_tracker.id,
            }
        )
