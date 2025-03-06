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
    "name": "Website My Events",
    "summary": "My events in website portal",
    "version": "17.0.1.0.0",
    "category": "Events",
    "website": "https://github.com/tawasta/event",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["portal", "event", "website_event_cancellation"],
    "data": [
        "security/ir.model.access.csv",
        "views/event_portal_template_home.xml",
        "views/event_portal_template_menu.xml",
        "views/event_portal_template_my.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_my_events/static/src/js/registration.esm.js",
        ],
    },
}
