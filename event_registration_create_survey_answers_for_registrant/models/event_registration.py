from odoo import models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def action_launch_survey_user_input_creation(self):
        self.ensure_one()

        return {
            "name": "Create Survey Answer",
            "type": "ir.actions.act_window",
            "res_model": "survey.user.input.creation.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_event_registration_id": self.id,
            },
        }
