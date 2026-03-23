from odoo import models


class EventEvent(models.Model):
    _inherit = "event.event"

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
