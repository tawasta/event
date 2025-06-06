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
    "name": "Event Batch",
    "summary": "Allows creating student batches for event registrations",
    "version": "17.0.1.0.1",
    "category": "Website",
    "website": "https://github.com/tawasta/event",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "event",
        "event_sale",
        "openeducat_core",
        "society_batch_core",
        "society_student_core",
        "partner_event",
    ],
    "data": [
        "views/batch_students_view.xml",
        "views/product_views.xml",
        "views/student_views.xml",
        "views/event_views.xml",
    ],
}
