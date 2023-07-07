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
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.survey.controllers.main import Survey

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class SurveyFeedbackEvent(Survey):
    @http.route(
        "/survey/start/<string:survey_token>/event/<int:event_id>",
        type="http",
        auth="public",
        website=True,
    )
    def survey_start_event(
        self, survey_token, event_id=None, answer_token=None, email=False, **post
    ):
        """Start a survey by providing
        * a token linked to a survey;
        * a token linked to an answer or generate a new token if access is allowed;
        """
        # Get the current answer token from cookie
        answer_from_cookie = False
        if not answer_token:
            answer_token = request.httprequest.cookies.get("survey_%s" % survey_token)
            answer_from_cookie = bool(answer_token)

        access_data = self._get_access_data(
            survey_token, answer_token, ensure_token=False
        )

        if answer_from_cookie and access_data["validity_code"] in (
            "answer_wrong_user",
            "token_wrong",
        ):
            # If the cookie had been generated for another user or does not correspond
            # to any existing answer object (probably because it has been deleted),
            # ignore it and redo the check. The cookie will be replaced by a legit
            # value when resolving the URL, so we don't clean it further here.
            access_data = self._get_access_data(survey_token, None, ensure_token=False)

        if access_data["validity_code"] is not True:
            return self._redirect_with_error(access_data, access_data["validity_code"])

        survey_sudo, answer_sudo = (
            access_data["survey_sudo"],
            access_data["answer_sudo"],
        )
        if not answer_sudo:
            try:
                answer_sudo = survey_sudo._create_answer(user=False, email=False)
            except UserError:
                answer_sudo = False

        if not answer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access_rights("read")
                survey_sudo.with_user(request.env.user).check_access_rule("read")
            except Exception:
                return request.redirect("/")
            else:
                return request.render("survey.survey_403_page", {"survey": survey_sudo})

        if event_id:
            event = request.env["event.event"].sudo().search([("id", "=", event_id)])
            answer_sudo.sudo().write({"event_id": event.id})
            return request.redirect(
                "/survey/%s/%s/event/%s"
                % (survey_sudo.access_token, answer_sudo.access_token, event_id)
            )

    @http.route(
        "/survey/<string:survey_token>/<string:answer_token>/event/<int:event_id>",
        type="http",
        auth="public",
        website=True,
    )
    def survey_event_display_page(self, survey_token, answer_token, **post):
        return super(SurveyFeedbackEvent, self).survey_display_page(
            survey_token, answer_token, **post
        )
