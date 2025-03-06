##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (http://www.futural.fi)
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
    "name": "Website Event Cancellation",
    "summary": "Cancel events and event registrations through website.",
    "version": "17.0.1.0.3",
    "category": "Events",
    "website": "https://github.com/tawasta/event",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mail_template_name_translatable",
        "website_event",
        # "website_event_frontend_customization",
        "email_template_qweb",
    ],
    "data": [
        "views/event_views.xml",
        "views/event_stage_views.xml",
        "views/event_templates_page_cancellation.xml",
        "views/event_templates_page_registration.xml",
        "views/event_templates_list.xml",
        "data/email_template_views.xml",
        "data/email_template_data.xml",
        # File below is not used yet
        "data/event_data.xml",
    ],
}
