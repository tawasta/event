import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    company_name = fields.Char(compute="_compute_company_name", store=True)

    @api.depends(
        "survey_answer_ids",
        "survey_answer_ids.user_input_line_ids",
        "survey_answer_ids.user_input_line_ids.question_id",
        "survey_answer_ids.user_input_line_ids.question_id.save_as_event_registration_company_name",
        "survey_answer_ids.user_input_line_ids.value_char_box",
    )
    def _compute_company_name(self):
        # Override the default computations of event and partner_event so that
        # _synchronize_partner_values() is not called anymore and the company_name
        # field is fetched from survey answers instead
        for registration in self:
            company_name_answers = registration.survey_answer_ids.mapped(
                "user_input_line_ids"
            ).filtered(
                lambda line: line.question_id.save_as_event_registration_company_name
            )

            if company_name_answers:
                registration.company_name = company_name_answers[0].value_char_box
            else:
                registration.company_name = "-"
