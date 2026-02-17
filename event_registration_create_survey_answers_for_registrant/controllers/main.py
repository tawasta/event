import logging

from odoo import http
from odoo.http import request

from odoo.addons.survey.controllers.main import Survey

_logger = logging.getLogger(__name__)


class SurveyAnswerForRegistrant(Survey):
    @http.route()
    def survey_submit(self, survey_token, answer_token, **post):
        """ """

        _logger.info("Survey submit reached with: ")
        _logger.info(survey_token)
        _logger.info(answer_token)
        _logger.info(post)
        _logger.info("--")

        _logger.info("res and ctx:")
        res = super().survey_submit(survey_token, answer_token, **post)
        _logger.info(res)
        _logger.info(request.env.context)
        _logger.info("--")

        access_data = self._get_access_data(
            survey_token, answer_token, ensure_token=True
        )

        answer_sudo = access_data["answer_sudo"]

        _logger.info("answer record:")
        _logger.info(answer_sudo)

        # If backend user added the answers, always mark them done right
        # after submission
        if answer_sudo.created_on_behalf_of_registrant:
            _logger.info("WAS created on behalf of registrant")

            answer_sudo._mark_done()

            # registration.write({
            #    "survey_answer_ids": [(4, answer_sudo.id)]
            # })

        else:
            _logger.info("was NOT created on behalf of registrant")

        return res
