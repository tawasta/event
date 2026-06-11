from odoo import _, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def action_send_company_invitation(self):
        """Open the email composer to send a company invitation to the attendee."""
        self.ensure_one()
        template = self.env.ref(
            "event_email_customization.event_company_invitation",
            raise_if_not_found=True,
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Send Company Invitation"),
            "res_model": "mail.compose.message",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_model": "event.registration",
                "default_res_ids": self.ids,
                "default_template_id": template.id,
                "default_composition_mode": "comment",
                "force_email": True,
            },
        }

    def action_send_moodle_invitation(self):
        """Open the email composer to send a moodle invitation to the attendee."""
        self.ensure_one()
        template = self.env.ref(
            "event_email_customization.event_moodle_invitation", raise_if_not_found=True
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Send Moodle Invitation"),
            "res_model": "mail.compose.message",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_model": "event.registration",
                "default_res_ids": self.ids,
                "default_template_id": template.id,
                "default_composition_mode": "comment",
                "force_email": True,
            },
        }
