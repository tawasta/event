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
from odoo import fields, models

_logger = logging.getLogger(__name__)

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class Survey(models.Model):
    # 1. Private attributes
    _inherit = "survey.survey"

    # 2. Fields declaration
    is_event_survey = fields.Boolean(
        "Is an Event Survey",
        help="If checked, this survey can be used as an Event Survey.",
    )

    default_survey = fields.Boolean(
        "Is default survey",
        help="If selected, this survey will be automatically selected when the "
        "event is created ",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def _create_answer(
        self,
        user=False,
        partner=False,
        email=False,
        test_entry=False,
        check_attempts=True,
        **additional_vals,
    ):
        """Extend core's answer creation to also save the respondent's first
        name, last name and phone number on the answer, mirroring what core
        already does for email/nickname (see save_as_email/save_as_nickname).
        """
        if user and not user._is_public():
            additional_vals.setdefault("firstname", user.firstname)
            additional_vals.setdefault("lastname", user.lastname)
            additional_vals.setdefault("phone", user.phone)
        elif partner:
            additional_vals.setdefault("firstname", partner.firstname)
            additional_vals.setdefault("lastname", partner.lastname)
            additional_vals.setdefault("phone", partner.phone)

        user_inputs = super()._create_answer(
            user=user,
            partner=partner,
            email=email,
            test_entry=test_entry,
            check_attempts=check_attempts,
            **additional_vals,
        )

        for question in self.mapped("question_ids").filtered(
            lambda q: q.question_type == "char_box"
            and (q.save_as_phone or q.save_as_firstname or q.save_as_lastname)
        ):
            for user_input in user_inputs:
                if question.save_as_firstname and user_input.firstname:
                    user_input._save_lines(question, user_input.firstname)
                if question.save_as_lastname and user_input.lastname:
                    user_input._save_lines(question, user_input.lastname)
                if question.save_as_phone and user_input.phone:
                    user_input._save_lines(question, user_input.phone)

        return user_inputs

    # 8. Business methods
