##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2023 Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
    "name": "Event Ticket Registration: Self or Invite Others",
    "summary": "Event Ticket Registration: Self or Invite Others",
    "version": "17.0.1.0.0",
    "category": "Event",
    "website": "https://gitlab.com/tawasta/odoo/event",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_event", "website_my_events"],
    "data": [
        "data/mail_template_data.xml",
        "data/mail_template_view.xml",
        "views/event_templates.xml",
        "views/event_view.xml",
        "views/registration_invitation.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_frontend": [
            "event_ticket_purchase_options/static/src/js/invitation.esm.js",
            "event_ticket_purchase_options/static/src/js/ticket.esm.js",
        ],
    },
}
