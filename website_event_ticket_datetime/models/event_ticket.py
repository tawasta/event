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

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTicket(models.Model):
    # 1. Private attributes
    _inherit = "event.event.ticket"

    # 2. Fields declaration
    start_sale_datetime = fields.Datetime(string="Registration Start")
    end_sale_datetime = fields.Datetime(string="Registration End")

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends(
        "is_expired",
        "start_sale_datetime",
        "event_id.date_tz",
        "seats_available",
        "seats_max",
    )
    def _compute_sale_available(self):
        return super(EventTicket, self)._compute_sale_available()

    @api.depends("end_sale_datetime", "event_id.date_tz")
    def _compute_is_expired(self):
        for ticket in self:
            ticket = ticket._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(
                ticket, fields.Datetime.now()
            )
            if ticket.end_sale_datetime:
                end_sale_datetime = fields.Datetime.context_timestamp(
                    ticket, ticket.end_sale_datetime
                )
                ticket.is_expired = end_sale_datetime < current_datetime
            else:
                ticket.is_expired = False

    # 5. Constraints and onchanges
    @api.constrains("start_sale_datetime", "end_sale_datetime")
    def _constrains_dates_coherency(self):
        return super(EventTicket, self)._constrains_dates_coherency()

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    def is_launched(self):
        # TDE FIXME: in master, make a computed field, easier to use
        self.ensure_one()
        if self.start_sale_datetime:
            ticket = self._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(
                ticket, fields.Datetime.now()
            )
            start_sale_datetime = fields.Datetime.context_timestamp(
                ticket, ticket.start_sale_datetime
            )
            return start_sale_datetime <= current_datetime
        else:
            return True
