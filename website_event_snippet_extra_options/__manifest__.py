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
    "name": "Website 'Events' Snippet Extra Options",
    "summary": "Additional configurations for the core snippet",
    "version": "17.0.1.0.1",
    "category": "Event",
    "website": "https://github.com/tawasta/event",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_event_private_event"],
    "data": [
        "views/event_event_views.xml",
        "views/snippets/s_events_extended.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_event/static/src/snippets/s_events/000.js",
            "website_event_snippet_extra_options/static/src/"
            "snippets/s_events_extended/000.esm.js",
        ]
    },
}
