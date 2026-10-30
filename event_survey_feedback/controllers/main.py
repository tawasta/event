##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
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
# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.survey.controllers.main import Survey

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class SurveyEventFeedback(Survey):
    def _start_event_feedback_survey(
        self,
        survey_token,
        event_id,
        registration_id=None,
        answer_token=None,
        email=False,
        **post,
    ):
        """Stash event/registration context, then delegate to core's survey_start.

        The event (and registration, if known) are attached through the
        environment context so :meth:`survey.survey._create_answer` can set
        them at creation time, instead of duplicating core's logic.

        :param str survey_token: access token of the feedback survey
        :param int event_id: event this feedback answer belongs to
        :param int registration_id: attendee this feedback answer was
            requested from, if the link was sent for a specific
            registration; must belong to ``event_id``, otherwise ignored
        :param str answer_token: access token of an existing answer, if any
        :param str email: email of the respondent, if not logged in
        """
        event = request.env["event.event"].sudo().browse(event_id).exists()
        if event:
            request.update_context(event_survey_feedback_event_id=event.id)
            if registration_id:
                registration = (
                    request.env["event.registration"]
                    .sudo()
                    .browse(registration_id)
                    .exists()
                    .filtered(lambda r: r.event_id == event)
                )
                if registration:
                    request.update_context(
                        event_survey_feedback_registration_id=registration.id
                    )
        return self.survey_start(
            survey_token, answer_token=answer_token, email=email, **post
        )

    @http.route(
        "/survey/start/<string:survey_token>/event/<int:event_id>"
        "/registration/<int:registration_id>",
        type="http",
        auth="public",
        website=True,
    )
    def survey_start_event_registration(
        self,
        survey_token,
        event_id,
        registration_id,
        answer_token=None,
        email=False,
        **post,
    ):
        """Feedback link sent for one specific attendee (the usual case).

        See :meth:`_start_event_feedback_survey`.
        """
        return self._start_event_feedback_survey(
            survey_token,
            event_id,
            registration_id=registration_id,
            answer_token=answer_token,
            email=email,
            **post,
        )

    @http.route(
        "/survey/start/<string:survey_token>/event/<int:event_id>",
        type="http",
        auth="public",
        website=True,
    )
    def survey_start_event(
        self, survey_token, event_id, answer_token=None, email=False, **post
    ):
        """Feedback link shared generically for an event (no specific attendee).

        See :meth:`_start_event_feedback_survey`.
        """
        return self._start_event_feedback_survey(
            survey_token, event_id, answer_token=answer_token, email=email, **post
        )
