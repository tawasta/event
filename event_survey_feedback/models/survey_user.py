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


class SurveyUserInput(models.Model):
    # 1. Private attributes
    _inherit = "survey.user_input"

    # 2. Fields declaration
    feedback_event_id = fields.Many2one(
        "event.event",
        string="Feedback Event",
        readonly=True,
        store=True,
        help="Event this feedback survey answer relates to. Deliberately "
        "separate from any registration-survey event link, so this module "
        "does not depend on how (or whether) attendees registered.",
    )
    feedback_registration_id = fields.Many2one(
        "event.registration",
        string="Feedback Registration",
        readonly=True,
        store=True,
        help="Attendee this feedback answer was requested from, when the "
        "feedback link was sent for a specific registration rather than "
        "shared generically for the event.",
    )
