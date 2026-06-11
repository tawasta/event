from odoo import models


class WaitingMailListWizard(models.TransientModel):
    _inherit = "website.event.waiting.mail.list.wizard"

    def send_confirmation_mail(self):
        """Send waiting list confirmation using our custom template."""
        self.ensure_one()
        msg_template = self.env.ref(
            "event_email_customization.event_confirm_waiting_custom",
            raise_if_not_found=False,
        )
        if not msg_template:
            # Fallback to base if something is wrong
            return super().send_confirmation_mail()

        registration_ids_sent = []
        for registration in self.registration_ids:
            if registration.email and registration.waiting_list_to_confirm:
                registration_ids_sent.append(registration.id)
                msg_template.sudo().send_mail(registration.id, force_send=True)

        message_vals = {
            "message": "Waiting list confirmation mail "
            "sent to following registrations:",
            "registration_ids": registration_ids_sent,
        }
        message = self.env["website.event.waiting.mail.list.message"].create(
            message_vals
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "website.event.waiting.mail.list.message",
            "view_mode": "form",
            "res_id": message.id,
            "target": "new",
        }
