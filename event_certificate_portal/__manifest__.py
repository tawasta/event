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
    "name": "Event Certificate Portal",
    "summary": (
        "Attendance certificates for events with portal download "
        "and post-event email sending"
    ),
    "version": "17.0.1.0.1",
    "category": "event",
    "website": "https://github.com/tawasta/event",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "event",
        "website_event",
        "website_my_events",
        "portal",
        "mail",
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/paperformat.xml",
        "report/event_certificate_report.xml",
        "data/mail_template.xml",
        "data/ir_cron.xml",
        "views/res_company_views.xml",
        "views/event_event_views.xml",
        "views/event_registration_views.xml",
        "views/portal_templates.xml",
    ],
    "demo": [],
}
