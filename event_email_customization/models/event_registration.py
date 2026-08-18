from odoo import _, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def send_moodle(self):
        """
        Override to use our custom mail template instead of the original
        connector_moodle template. All other logic remains identical.
        """
        for rec in self:
            course = rec.event_id.moodle_course_id
            if not course:
                continue

            # Use our custom template instead of the original
            mail_template = rec.env.ref(
                "event_email_customization.event_moodle_invitation_custom"
            ).sudo()
            if not mail_template:
                continue

            if rec.moodle_info_sent:
                continue

            partner = rec.attendee_partner_id
            if not partner:
                partner = rec.partner_id

            invite_others = hasattr(rec, "invite_others") and rec.invite_others
            used = hasattr(rec, "invite_id") and rec.invite_id and rec.invite_id.is_used

            if rec.state == "open":
                if not invite_others or (invite_others and used):
                    # Send to Moodle if not draft registrations
                    # OR draft registration but used
                    rec.env["moodle.binding"].sudo().with_context(
                        lang="fi_FI"
                    ).enrol_user_sale(partner, course)

                    email_values = {
                        "email_to": rec.email,
                        "auto_delete": True,
                        "message_type": "email",
                        "recipient_ids": [],
                        "partner_ids": [],
                    }

                    try:
                        mail_template.send_mail(
                            rec.id,
                            force_send=True,
                            raise_exception=True,
                            email_values=email_values,
                        )
                        body = (
                            "An email containing Moodle course info "
                            f"has been sent to: {rec.email}."
                        )
                        rec.sudo().message_post(
                            body=body,
                            subject=_("Course info sent"),
                            subtype_xmlid="mail.mt_note",
                            message_type="notification",
                        )
                        rec.sudo().write({"moodle_info_sent": True})
                    except Exception:
                        continue
