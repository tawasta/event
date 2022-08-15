##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2018 Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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
    "name": "Website Event Track Privacy Values",
    "summary": "Website event track privacy values",
    "version": "14.0.1.0.3",
    "category": "Event",
    "website": "https://gitlab.com/tawasta/odoo/event",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_event_track_advanced",
        "event",
        "privacy",
        "privacy_consent",
        "partner_event",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/event_view.xml",
        "views/privacy_activity.xml",
        "views/templates.xml",
    ],
}
