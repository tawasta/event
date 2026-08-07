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
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventMail(models.Model):
    # 1. Private attributes
    _inherit = "event.mail"

    # 2. Fields declaration
    feedback_survey_id = fields.Many2one(
        string="Feedback survey",
        comodel_name="survey.survey",
        help="Overrides the event's own feedback survey for this scheduler, if set.",
    )

    # 8. Business methods
    def _get_feedback_survey(self):
        """Return the survey to assign, preferring this scheduler's override."""
        self.ensure_one()
        return self.feedback_survey_id or self.event_id.feedback_survey_id

    def _execute_event_based_for_registrations(self, registrations):
        """Tag ``registrations`` with the feedback survey before core sends the mail.

        Covers the event/slot-based flows; the attendee-based flow is
        covered separately in
        :meth:`event.mail.registration._execute_on_registrations`.
        """
        self.ensure_one()
        if self.template_ref.is_feedback_email:
            survey = self._get_feedback_survey()
            if survey:
                registrations.write({"feedback_survey_id": survey.id})
        return super()._execute_event_based_for_registrations(registrations)


class MailTemplate(models.Model):
    # 1. Private attributes
    _inherit = "mail.template"

    # 2. Fields declaration
    is_feedback_email = fields.Boolean(
        default=False,
        help="If enabled, sending this template to an event registration "
        "sets the recipient's feedback survey.",
    )
