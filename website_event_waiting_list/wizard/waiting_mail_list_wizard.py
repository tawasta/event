from odoo import fields, models
from odoo.http import request


class WaitingMailListWizard(models.TransientModel):
    # 1. Private attributes
    _name = "website.event.waiting.mail.list.wizard"
    _description = "Mail confirmation email to waiting list contacts"

    # 2. Fields declaration
    registration_ids = fields.Many2many(
        "event.registration",
        default=lambda self: self.env["event.registration"].browse(
            self._context.get("active_ids")
        ),
        string="Registrations",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def send_confirmation_mail(self):
        self.ensure_one()
        msg_template = request.env.ref(
            "website_event_waiting_list.event_confirm_waiting_registration"
        )
        registration_ids_sent = []
        for registration in self.registration_ids:
            if registration.email and registration.waiting_list_to_confirm:
                registration_ids_sent.append(registration.id)
                msg_template.sudo().send_mail(registration.id, force_send=True)

        message = self.env["website.event.waiting.mail.list.message"].create(
            {
                "message": "Waiting list confirmation mail sent to following registrations:",
                "registration_ids": registration_ids_sent,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "website.event.waiting.mail.list.message",
            "view_type": "form",
            "view_mode": "form",
            "res_id": message.id,
            "target": "new",
        }

    # 8. Business methods
