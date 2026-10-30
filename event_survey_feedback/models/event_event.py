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
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    feedback_survey_id = fields.Many2one(
        string="Feedback survey", comodel_name="survey.survey"
    )
    survey_start_url = fields.Char("Feedback link", compute="_compute_survey_start_url")
    feedback_user_input_ids = fields.One2many(
        "survey.user_input",
        "feedback_event_id",
        string="Feedback Answers",
    )
    feedback_answer_count = fields.Integer(
        string="Feedback Answers",
        compute="_compute_feedback_answer_count",
    )

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("feedback_survey_id")
    def _compute_survey_start_url(self):
        for event in self:
            event.survey_start_url = (
                f"{event.get_base_url()}/survey/start/"
                f"{event.feedback_survey_id.access_token}/event/{event.id}"
                if event.feedback_survey_id
                else False
            )

    @api.depends("feedback_user_input_ids.state")
    def _compute_feedback_answer_count(self):
        counts = dict(
            self.env["survey.user_input"]._read_group(
                domain=[
                    ("feedback_event_id", "in", self.ids),
                    ("state", "=", "done"),
                ],
                groupby=["feedback_event_id"],
                aggregates=["__count"],
            )
        )
        for event in self:
            event.feedback_answer_count = counts.get(event, 0)
