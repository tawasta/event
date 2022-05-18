##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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

# 1. Standard library imports:
import pytz

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    start_sale_datetime = fields.Datetime(
        "Start sale datetime",
        compute="_compute_start_sale_datetime",
        help="If ticketing is used, contains the earliest starting sale date of tickets.",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_ticket_ids.start_sale_datetime")
    def _compute_start_sale_datetime(self):
        """Compute the start sale date of an event. Currently lowest starting sale
        date of tickets if they are used, of False."""
        for event in self:
            start_dates = [
                ticket.start_sale_datetime
                for ticket in event.event_ticket_ids
                if not ticket.is_expired
            ]
            event.start_sale_datetime = (
                min(start_dates) if start_dates and all(start_dates) else False
            )

    @api.depends(
        "date_tz",
        "start_sale_datetime",
        "date_end",
        "seats_available",
        "seats_limited",
        "event_ticket_ids.sale_available",
    )
    def _compute_event_registrations_open(self):
        """Compute whether people may take registrations for this event
        * event.date_end -> if event is done, registrations are not open anymore;
        * event.start_sale_datetime -> lowest start date of tickets (if any; start_sale_date
          is False if no ticket are defined, see _compute_start_sale_date);
        * any ticket is available for sale (seats available) if any;
        * seats are unlimited or seats are available;
        """
        for event in self:
            event = event._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(
                event, fields.Datetime.now()
            )
            date_end_tz = (
                event.date_end.astimezone(pytz.timezone(event.date_tz or "UTC"))
                if event.date_end
                else False
            )
            event.event_registrations_open = (
                (
                    event.start_sale_datetime <= current_datetime.now()
                    if event.start_sale_datetime
                    else True
                )
                and (date_end_tz >= current_datetime if date_end_tz else True)
                and (not event.seats_limited or event.seats_available)
                and (
                    not event.event_ticket_ids
                    or any(ticket.sale_available for ticket in event.event_ticket_ids)
                )
            )

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
