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
# 2. Known third party imports:
# 3. Odoo imports (openerp):
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:
_logger = logging.getLogger(__name__)
# 6. Unknown third party imports:


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    survey_ids = fields.Many2many("survey.survey", string="Survey")

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    survey_ids = fields.Many2many(
        "survey.survey",
        string="Survey",
        readonly=False,
        store=True,
        compute="_compute_survey_ids",
        default=lambda self: self.env["survey.survey"]
        .sudo()
        .search([("default_survey", "=", True), ("is_event_survey", "=", True)])
        .ids,
    )
    answer_sheet_count = fields.Integer(
        string="Number of Answer Sheets",
        store=True,
        readonly=True,
        compute="_compute_answer_sheet_count",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_type_id")
    def _compute_survey_ids(self):
        """Copy the default survey from the event type when it changes."""
        for event in self:
            if not event.survey_ids and event.event_type_id.survey_ids:
                event.survey_ids = event.event_type_id.survey_ids

    @api.depends("survey_ids.user_input_ids")
    def _compute_answer_count(self):
        counts = dict(
            self.env["survey.user_input.line"]._read_group(
                domain=[
                    ("event_id", "in", self.ids),
                    ("registration_id.state", "!=", "cancel"),
                ],
                groupby=["event_id"],
                aggregates=["__count"],
            )
        )
        for event in self:
            event.answer_count = counts.get(event, 0)

    @api.depends("survey_ids.user_input_ids")
    def _compute_answer_sheet_count(self):
        counts = dict(
            self.env["survey.user_input"]._read_group(
                domain=[
                    ("event_id", "in", self.ids),
                    ("registration_id.state", "!=", "cancel"),
                ],
                groupby=["event_id"],
                aggregates=["__count"],
            )
        )
        for event in self:
            event.answer_sheet_count = counts.get(event, 0)

    # 5. Constraints and onchanges
    @api.constrains("survey_ids")
    def _check_survey_has_basic_questions(self):
        for event in self:
            if event.survey_ids:
                counters = {
                    "firstname_count": 0,
                    "lastname_count": 0,
                    "email_count": 0,
                    "phone_count": 0,
                }
                for survey in event.survey_ids:
                    if len(survey.question_ids) < 1:
                        raise ValidationError(
                            self.env._(
                                "Event Survey(s) needs to include at least one "
                                "question."
                            )
                        )
                    for question in survey.question_ids:
                        if question.save_as_firstname:
                            counters["firstname_count"] += 1
                        if question.save_as_lastname:
                            counters["lastname_count"] += 1
                        if question.save_as_email:
                            counters["email_count"] += 1
                        if question.save_as_phone:
                            counters["phone_count"] += 1
                if any(i < 1 for i in counters.values()):
                    raise ValidationError(
                        self.env._(
                            "Event Survey(s) needs to include questions asking for "
                            "the registrants first name, last name, email and "
                            "phone number. One of these questions is missing."
                        )
                    )
                elif any(i > 1 for i in counters.values()):
                    raise ValidationError(
                        self.env._(
                            "Event Survey(s) can only have one question "
                            "for the registrants first name, last name, email and "
                            "phone number. One of these questions has a duplicate."
                        )
                    )

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
