##############################################################################
#
#    Author: Futural Oy
#    Copyright 2026- Futural Oy (https://futural.fi)
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
    "name": "Event Email Customization",
    "version": "17.0.1.0.3",
    "summary": "Custom event messaging emails",
    "category": "Marketing/Events",
    "author": "Futural",
    "website": "https://github.com/tawasta/event",
    "license": "LGPL-3",
    "depends": [
        "event",
        "website_event_waiting_list",
        "website_event_cancellation",
        "event_ticket_purchase_options",
        "connector_moodle",
    ],
    "data": [
        "data/registration_views.xml",
        "data/registration_views_en.xml",
        "data/reminder_views.xml",
        "data/reminder_views_en.xml",
        "data/waiting_list_views.xml",
        "data/waiting_list_views_en.xml",
        "data/mail_templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
