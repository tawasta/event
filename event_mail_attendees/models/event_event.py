from odoo import models


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def action_message_attendees(self):
        self.ensure_one()
        template = self.env.ref(
            "event_mail_attendees.event_mail_template_mail_attendees",
            raise_if_not_found=False,
        )
        local_context = dict(
            self.env.context,
            default_event_id=self.id,
            default_template_id=template and template.id or False,
        )
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "event.mail.attendees.wizard",
            "target": "new",
            "context": local_context,
        }

    # 8. Business methods
