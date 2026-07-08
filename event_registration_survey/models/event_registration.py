##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################
# 1. Standard library imports:
import logging

# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


def _extract_comment_from_answers(question, answers):
    """Split raw posted answers from their optional comment.

    Copied from ``survey.controllers.main.Survey._extract_comment_from_answers``
    (a pure function of its arguments, no request/self usage) so this model
    does not need to instantiate the survey HTTP controller class to reach it.
    """
    comment = None
    answers_no_comment = []
    if answers:
        if question.question_type == "matrix":
            if "comment" in answers:
                comment = answers["comment"].strip()
                answers.pop("comment")
            answers_no_comment = answers
        else:
            if not isinstance(answers, list):
                answers = [answers]
            for answer in answers:
                if isinstance(answer, dict) and "comment" in answer:
                    comment = answer["comment"].strip()
                else:
                    answers_no_comment.append(answer)
            if len(answers_no_comment) == 1:
                answers_no_comment = answers_no_comment[0]
    return answers_no_comment, comment


class EventRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
    survey_answer_ids = fields.Many2many(
        "survey.user_input", string="Survey User Input", readonly=True
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    def _process_question(self, question, answers, answer_sudo):
        """
        Checks question for validity,
        saves question line and returns an answer upon success.
        """
        inactive_questions = (
            self.env["survey.question"]
            if answer_sudo.is_session_answer
            else answer_sudo._get_inactive_conditional_questions()
        )
        # skip if question is inactive
        if question in inactive_questions:
            return
        answer, comment = _extract_comment_from_answers(question, answers)
        error = question.validate_question(answer, comment)
        if not error.get(question.id):
            answer_sudo._save_lines(question, answer, comment)
            return answer
        _logger.info("Invalid question: %s", question)
        return False

    def _prepare_submit_answer_matrix(
        self, params, question_id, row_id, col_id, is_comment
    ):
        if question_id not in params:
            params[question_id] = {}
        if is_comment:
            params[question_id]["comment"] = col_id
        else:
            if row_id not in params[question_id]:
                params[question_id][row_id] = []
            params[question_id][row_id].append(col_id)
        return params

    def process_survey(self, registration_id, survey_info):
        registration = self.browse(registration_id)

        if not registration.partner_id:
            raise RetryableJobError(
                _("Registration does not have an associated partner.")
            )
        answer_ids = []

        # Prepare survey_info for matrix questions. Matrix answers are posted
        # as "{question_id}_{row_id}" (a checked cell) or "{question_id}_comment"
        # (the free-text comment, see question_matrix in event_templates.xml);
        # only the former is a numeric row id.
        #
        # survey_info is the whole per-registration dict built by
        # _sort_form_details, keyed by survey counter (e.g. "1": {...}) for
        # actual survey answers, but also "event_ticket_id"/"event_id" as
        # plain string values (not a dict) alongside them - skip those here,
        # this method only deals with survey answers.
        new_survey_info = {}
        for survey_id, details in survey_info.items():
            if not isinstance(details, dict):
                continue
            new_details = {}
            for key, value in details.items():
                if "_" in key:
                    question_id_str, suffix = key.split("_", 1)
                    question_id = int(question_id_str)
                    if suffix == "comment":
                        new_details = self._prepare_submit_answer_matrix(
                            new_details, question_id, None, value, True
                        )
                    else:
                        new_details = self._prepare_submit_answer_matrix(
                            new_details, question_id, int(suffix), int(value), False
                        )
                else:
                    new_details[int(key)] = value
            new_survey_info[int(survey_id)] = new_details

        survey_info = new_survey_info

        # Fetch all surveys at once
        survey_ids = list(map(int, survey_info.keys()))
        surveys = self.env["survey.survey"].sudo().browse(survey_ids)

        for survey in surveys:
            if not survey.exists():
                raise ValidationError(_("Survey not found."))

            survey_details = survey_info.get(survey.id)
            if survey_details is None:
                _logger.error("Survey details not found for survey ID %s", survey.id)
                continue

            answer_sudo = survey._create_answer(user=self.env.user, test_entry=False)

            # Fetch all questions at once
            question_ids = [
                int(key) for key in survey_details.keys() if isinstance(key, int)
            ]
            questions = self.env["survey.question"].sudo().browse(question_ids)

            for question in questions:
                answer = self._process_question(
                    question, survey_details.get(question.id), answer_sudo
                )
                if answer:
                    _logger.debug("Saved answer for question %s: %s", question.id, answer)

            # Update the answer info and mark it done
            answer_sudo.write(
                {
                    "event_ticket_id": registration.event_ticket_id.id,
                    "event_id": registration.event_id.id,
                    "registration_id": registration.id,
                }
            )
            answer_sudo._mark_done()

            answer_ids.append(answer_sudo.id)

        # Link all answers to the registration
        registration.write(
            {
                "survey_answer_ids": [(6, 0, answer_ids)],
            }
        )
