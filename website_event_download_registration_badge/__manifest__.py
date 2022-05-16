##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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
    "name": "Website Event Download Registration Badge",
    "summary": "Ability to navigate to an URL and download Registration Badge",
    "description": "Ability to navigate to an URL and download Registration Badge",
    "version": "14.0.1.0.1",
    "category": "Events",
    "website": "https://gitlab.com/tawasta/odoo/event",
    "author": "Miika Nissi",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_event_cancellation",
        "website_event_track_privacies",
        "website_event_questions",
    ],
    "data": [
        "data/email_template_views.xml",
        "views/event_registration_views.xml",
        "views/templates.xml",
    ],
}
