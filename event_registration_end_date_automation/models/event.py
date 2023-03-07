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
import logging
from datetime import datetime

# 2. Known third party imports:
import pytz
from dateutil.relativedelta import relativedelta

# 3. Odoo imports (openerp):
from odoo import api, fields, models
from odoo.tools import format_datetime

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)

_INTERVALS = {
    "hours": lambda interval: relativedelta(hours=interval),
    "days": lambda interval: relativedelta(days=interval),
    "weeks": lambda interval: relativedelta(days=7 * interval),
}


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    has_end_date = fields.Boolean(
        "Registration end date",
        default=False,
    )
    end_interval_nbr = fields.Integer("Interval", default=1)
    end_interval_unit = fields.Selection(
        [("days", "Days")],
        string="Unit",
        default="days",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    has_end_date = fields.Boolean(
        "Registration end date",
        compute="_compute_has_end",
        help="Allows registrants to cancel their registrations.",
        default=False,
        readonly=False,
        store=True,
    )
    end_interval_nbr = fields.Integer(
        string="Interval",
        compute="_compute_end_interval_nbr",
        default=1,
        required=False,
        readonly=False,
        store=True,
    )
    end_interval_unit = fields.Selection(
        [("days", "Days")],
        string="Unit",
        compute="_compute_end_interval_unit",
        default="days",
        required=False,
        readonly=False,
        store=True,
    )
    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_type_id", "has_end_date")
    def _compute_has_end(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            event.has_end_date = event.event_type_id.has_end_date


    @api.depends("event_type_id")
    def _compute_end_interval_nbr(self):
        for event in self:
            if not event.event_type_id:
                event.end_interval_nbr = event.end_interval_nbr or 0
            else:
                event.end_interval_nbr = event.event_type_id.end_interval_nbr or 0

    @api.depends("event_type_id")
    def _compute_end_interval_unit(self):
        for event in self:
            if not event.event_type_id:
                event.end_interval_unit = event.end_interval_unit or "days"
            else:
                event.end_interval_unit = (
                    event.event_type_id.end_interval_unit or "days"
                )

    def write(self, vals):
        res = super(EventEvent, self).write(vals)
        if "has_end_date" in vals and vals.get("has_end_date"):
            for ticket in self.event_ticket_ids:
                new_end_date = ticket.end_sale_datetime - relativedelta(days=self.end_interval_nbr)
                ticket.sudo().write({"end_sale_datetime": new_end_date})
        return res

    @api.model
    def create(self, vals):
        record = super(EventEvent, self).create(vals)
        if "has_end_date" in vals and vals.get("has_end_date"):
            for ticket in self.event_ticket_ids:
                new_end_date = ticket.end_sale_datetime - relativedelta(days=self.end_interval_nbr)
                ticket.sudo().write({"end_sale_datetime": new_end_date})
        return record

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
