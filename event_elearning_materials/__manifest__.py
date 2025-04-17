##############################################################################
#
#    Author: Tawasta
#    Copyright 2020 Futural Oy (https://futural.fi)
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
    "name": "Event eLearning Integration",
    "summary": "Link eLearning materials to events and share them with attendees.",
    "version": "17.0.1.0.1",
    "category": "Website",
    "website": "https://github.com/tawasta/event",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "event",
        "website_slides",
        "website_event_cancellation",
    ],
    "data": [
        "data/mail_template_view.xml",
        "views/event_views.xml",
    ],
}
