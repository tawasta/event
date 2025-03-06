##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2025- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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
    "name": "Website Event: RSS Multi-tag Feed",
    "summary": "Ability to create custom RSS Feeds with events of multiple event tags",
    "version": "17.0.1.0.2",
    "category": "Events",
    "website": "https://github.com/tawasta/event",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_event"],
    "data": [
        "security/ir.model.access.csv",
        "views/event_multifeed_views.xml",
        "views/event_multifeed_templates.xml",
    ],
}
