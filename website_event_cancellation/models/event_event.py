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
    has_cancel = fields.Boolean(
        "Allow Cancellations",
        help="Allows registrants to cancel their registrations.",
        default=True,
        tracking=True,
    )
    cancel_interval_nbr = fields.Integer("Interval", default=1)
    cancel_interval_unit = fields.Selection(
        [("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")],
        string="Unit",
        default="hours",
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
    has_cancel = fields.Boolean(
        "Allow Cancellations",
        compute="_compute_has_cancel",
        help="Allows registrants to cancel their registrations.",
        default=True,
        readonly=False,
        store=True,
    )
    cancel_interval_nbr = fields.Integer(
        string="Interval",
        compute="_compute_cancel_interval_nbr",
        default=1,
        required=False,
        readonly=False,
        store=True,
    )
    cancel_interval_unit = fields.Selection(
        [("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")],
        string="Unit",
        compute="_compute_cancel_interval_unit",
        default="days",
        required=False,
        readonly=False,
        store=True,
    )
    cancel_before_date = fields.Datetime(
        "Cancel registration before date", compute="_compute_before_date", store=True
    )
    able_to_cancel = fields.Boolean(
        "Able to cancel registration", compute="_compute_able_to_cancel", readonly=True
    )
    date_begin_calendar_utc = fields.Char(
        string="Start Date Calendar UTC", compute="_compute_date_begin_calendar_utc"
    )
    date_end_calendar_utc = fields.Char(
        string="End Date Calendar UTC", compute="_compute_date_end_calendar_utc"
    )
    date_begin_calendar_locale = fields.Char(
        string="Start Date Calendar Locale",
        compute="_compute_date_begin_calendar_locale",
    )
    date_end_calendar_locale = fields.Char(
        string="End Date Calendar Locale", compute="_compute_date_end_calendar_locale"
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_type_id", "has_cancel")
    def _compute_has_cancel(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            event.has_cancel = event.event_type_id.has_cancel

    @api.depends("date_tz", "date_begin")
    def _compute_date_begin_calendar_utc(self):
        for event in self:
            if event.date_begin:
                event.date_begin_calendar_utc = format_datetime(
                    self.env,
                    event.date_begin,
                    tz="UTC",
                    dt_format="yyyyMMdd'T'HHmmss'Z'",
                )
            else:
                event.date_begin_calendar_utc = False

    @api.depends("date_tz", "date_end")
    def _compute_date_end_calendar_utc(self):
        for event in self:
            if event.date_end:
                event.date_end_calendar_utc = format_datetime(
                    self.env, event.date_end, tz="UTC", dt_format="yyyyMMdd'T'HHmmss'Z'"
                )
            else:
                event.date_end_calendar_utc = False

    @api.depends("date_tz", "date_begin")
    def _compute_date_begin_calendar_locale(self):
        for event in self:
            if event.date_begin:
                event.date_begin_calendar_locale = format_datetime(
                    self.env,
                    event.date_begin,
                    tz=self._context.get("tz"),
                    dt_format="yyyyMMdd'T'HHmmss'Z'",
                )
            else:
                event.date_begin_calendar_locale = False

    @api.depends("date_tz", "date_end")
    def _compute_date_end_calendar_locale(self):
        for event in self:
            if event.date_end:
                event.date_end_calendar_locale = format_datetime(
                    self.env,
                    event.date_end,
                    tz=self._context.get("tz"),
                    dt_format="yyyyMMdd'T'HHmmss'Z'",
                )
            else:
                event.date_end_calendar_locale = False

    @api.depends("cancel_before_date", "date_end", "date_tz", "date_begin")
    def _compute_able_to_cancel(self):
        for event in self:
            if not event.has_cancel or datetime.now(
                tz=pytz.timezone(event.date_tz or "UTC")
            ) > event.cancel_before_date.astimezone(
                pytz.timezone(event.date_tz or "UTC")
            ):
                event.able_to_cancel = False
            else:
                event.able_to_cancel = True

    @api.depends("event_type_id")
    def _compute_cancel_interval_nbr(self):
        for event in self:
            if not event.event_type_id:
                event.cancel_interval_nbr = event.cancel_interval_nbr or 0
            else:
                event.cancel_interval_nbr = event.event_type_id.cancel_interval_nbr or 0

    @api.depends("event_type_id")
    def _compute_cancel_interval_unit(self):
        for event in self:
            if not event.event_type_id:
                event.cancel_interval_unit = event.cancel_interval_unit or "days"
            else:
                event.cancel_interval_unit = (
                    event.event_type_id.cancel_interval_unit or "days"
                )

    @api.depends(
        "cancel_interval_unit",
        "cancel_interval_nbr",
        "date_end",
        "date_begin",
        "able_to_cancel",
    )
    def _compute_before_date(self):
        for event in self:
            date, sign = event.date_begin, -1
            cancel_interval_unit = event.cancel_interval_unit or "hours"
            cancel_interval_nbr = event.cancel_interval_nbr or 1
            event.cancel_before_date = (
                date + _INTERVALS[cancel_interval_unit](sign * cancel_interval_nbr)
                if date
                else None
            )

    @api.depends(
        "date_tz",
        "event_registrations_started",
        "date_end",
        "seats_available",
        "seats_limited",
        "seats_max",
        "event_ticket_ids.sale_available",
    )
    def _compute_event_registrations_open(self):
        """If Event stage is cancelled close registrations"""
        for event in self:
            res = super()._compute_event_registrations_open()
            if event.stage_id.cancel:
                event.event_registrations_open = False
            return res

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
