from odoo import models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def write(self, vals):
        res = super().write(vals)

        if vals.get("state") == "done":
            self._mark_event_registration_done_from_feedback()

        return res

    def _mark_event_registration_done_from_feedback(self):
        for answer in self.sudo():
            registration = answer.registration_id

            if not registration:
                continue

            if not registration.feedback_survey_id:
                continue

            if answer.survey_id != registration.feedback_survey_id:
                continue

            if registration.state != "done":
                registration.action_set_done()