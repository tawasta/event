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


class EventMailRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.mail.registration"

    # 8. Business methods
    def _execute_on_registrations(self):
        """Tag registrations with the feedback survey before core sends the mail.

        Covers the attendee-based scheduler flow ('after each registration');
        the event-based and slot-based flows are covered separately in
        :meth:`event.mail._execute_event_based_for_registrations`.
        """
        todo = self.filtered(lambda r: r.scheduler_id.notification_type == "mail")
        for scheduler, reg_mails in todo.grouped("scheduler_id").items():
            if scheduler.template_ref.is_feedback_email:
                survey = scheduler._get_feedback_survey()
                if survey:
                    reg_mails.registration_id.write({"feedback_survey_id": survey.id})
        return super()._execute_on_registrations()
