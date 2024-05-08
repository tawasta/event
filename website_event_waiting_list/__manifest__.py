##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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
    "name": "Website Event Waiting List",
    "summary": "Adds a waiting list functionality to Events.",
    "version": "14.0.1.3.8",
    "category": "Events",
    "website": "https://gitlab.com/tawasta/odoo/event",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_event_cancellation", "website_event_ticket_datetime"],
    "data": [
        "wizard/waiting_mail_list_wizard.xml",
        "security/ir.model.access.csv",
        "data/email_template_views.xml",
        "data/email_template_data.xml",
        "views/assets.xml",
        "views/event_views.xml",
        "views/event_ticket_views.xml",
        "views/event_templates_page_registration.xml",
        "views/event_templates_page_waiting_list.xml",
        "wizard/waiting_mail_list_message.xml",
    ],
}
