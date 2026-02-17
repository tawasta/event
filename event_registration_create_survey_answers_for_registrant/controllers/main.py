import logging

from odoo import http

from odoo.addons.survey.controllers.main import Survey

_logger = logging.getLogger(__name__)


class SurveyAnswerForRegistrant(Survey):
    @http.route()
    def survey_submit(self, survey_token, answer_token, **post):
        # If backend user added the answers, always mark them done right
        # after submission
        res = super().survey_submit(survey_token, answer_token, **post)

        access_data = self._get_access_data(
            survey_token, answer_token, ensure_token=True
        )

        answer_sudo = access_data["answer_sudo"]

        if answer_sudo.created_on_behalf_of_registrant:
            answer_sudo._mark_done()

        return res
