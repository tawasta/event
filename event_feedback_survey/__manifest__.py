##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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
    "name": "Event Feedback Survey",
    "version": "14.0.1.0.0",
    "category": "Events",
    "summary": "Send automated event feedback survey mails",
    "website": "https://gitlab.com/tawasta/odoo/event",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["event", "email_template_qweb", "survey"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/event_portal_templates.xml",
        "views/event_views.xml",
        "views/survey_result_view.xml",
        "views/survey_user_views.xml",
        "data/email_template_views.xml",
        "data/email_template_data.xml",
    ],
}
