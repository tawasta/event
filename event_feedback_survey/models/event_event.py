##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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

import logging

import werkzeug

# 3. Odoo imports (openerp):
from odoo import fields, models, api

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    feedback_survey_id = fields.Many2one(
        string="Feedback survey", comodel_name="survey.survey"
    )

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
    feedback_survey_id = fields.Many2one(
        string="Feedback survey", comodel_name="survey.survey", readonly=False,
        store=True,
        compute="_compute_feedback_id",
    )

    feedback_link = fields.Char(
        "Feedback Link (URL)",
        help="Enter the URL address of a feedback survey.",
        readonly=False,
        compute="_compute_feedback_link",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_feedback_link(self):
        """Computes a public URL for the admission"""
        for event in self:
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            start_url = werkzeug.urls.url_join(
                event.get_base_url(),
                "/survey/start/%s/event/%s"
                % (event.feedback_survey_id.access_token, event.id),
            )

            logging.info(start_url)
            event.feedback_link = start_url

    @api.depends("event_type_id")
    def _compute_feedback_id(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if not event.feedback_survey_id and event.event_type_id.feedback_survey_id:
                event.feedback_survey_id = event.event_type_id.feedback_survey_id

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
