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
from odoo import models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class SurveySurvey(models.Model):
    # 1. Private attributes
    _inherit = "survey.survey"

    # 8. Business methods
    def _create_answer(
        self,
        user=False,
        partner=False,
        email=False,
        test_entry=False,
        check_attempts=True,
        **additional_vals,
    ):
        """Set feedback event/registration from context when starting a feedback survey.

        Set by :meth:`SurveyEventFeedback._start_event_feedback_survey`, so
        only ever present for feedback-survey answers.
        """
        event_id = self.env.context.get("event_survey_feedback_event_id")
        if event_id and "feedback_event_id" not in additional_vals:
            additional_vals["feedback_event_id"] = event_id
        registration_id = self.env.context.get("event_survey_feedback_registration_id")
        if registration_id and "feedback_registration_id" not in additional_vals:
            additional_vals["feedback_registration_id"] = registration_id
        return super()._create_answer(
            user=user,
            partner=partner,
            email=email,
            test_entry=test_entry,
            check_attempts=check_attempts,
            **additional_vals,
        )
