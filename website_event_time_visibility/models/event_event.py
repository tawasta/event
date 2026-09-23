##############################################################################
#
#    Author: Futural Oy
#    Copyright 2026 Futural Oy (https://futural.fi)
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

from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    show_time_on_website = fields.Boolean(
        string="Show Time on Website",
        default=True,
        help="Show the time of day for the start and end date on the "
        "website, in addition to the dates themselves. Disable this for "
        "e.g. self-paced online courses that start at a specific time "
        "but have no fixed end time of day.",
    )
