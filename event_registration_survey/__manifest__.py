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

{
    "name": "Event Registration Survey",
    "summary": "Use a Survey as the Event registration form",
    "version": "19.0.1.0.0",
    "category": "Events",
    "website": "https://github.com/tawasta/event",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web",
        "survey",
        "website_event_sale",
        "website_event_questions_view",
        "partner_firstname",
        "queue_job",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/queue_job_data.xml",
        "views/event_views.xml",
        "views/event_registration_attendee_details_template.xml",
        "views/event_templates.xml",
        "views/survey_question_views.xml",
        "views/survey_survey_views.xml",
        "views/survey_user_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "event_registration_survey/static/src/js/event_registration_survey.esm.js",
            "survey/static/src/scss/survey_templates_form.scss",
        ],
    },
}
