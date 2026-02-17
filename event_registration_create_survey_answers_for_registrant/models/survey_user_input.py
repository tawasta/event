import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    created_on_behalf_of_registrant = fields.Boolean(
        default=False,
        help="This participation's answers were filled in backend on behalf of the "
        "the registrant. ",
    )

    def write(self, values):
        res = super().write(values)

        _logger.info("user input write REACHED")
        _logger.info(self)
        _logger.info(values)
        _logger.info(self._context)
        _logger.info("--------------------------------")

        return res

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
