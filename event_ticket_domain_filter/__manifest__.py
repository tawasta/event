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
    "name": "Event Ticket Domain Filter",
    "summary": "Show event tickets only to users matching a partner domain.",
    "version": "17.0.1.2.1",
    "category": "Events",
    "website": "https://github.com/tawasta/event",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_event", "partner_domain_filter"],
    "data": [
        "views/event_views.xml",
        "views/templates.xml",
    ],
}
