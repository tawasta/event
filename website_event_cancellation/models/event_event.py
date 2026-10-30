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
from odoo import api, fields, models

CANCEL_INTERVAL_UNITS = [("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")]


class EventType(models.Model):
    _inherit = "event.type"

    has_cancel = fields.Boolean(
        "Allow Cancellations",
        help="Allows registrants to cancel their registrations.",
        default=True,
    )
    cancel_interval_nbr = fields.Integer("Interval", default=1)
    cancel_interval_unit = fields.Selection(
        CANCEL_INTERVAL_UNITS, string="Unit", default="days"
    )


class EventEvent(models.Model):
    _inherit = "event.event"

    has_cancel = fields.Boolean(
        "Allow Cancellations",
        compute="_compute_has_cancel",
        help="Allows registrants to cancel their registrations.",
        readonly=False,
        store=True,
    )
    cancel_interval_nbr = fields.Integer(
        string="Interval",
        compute="_compute_cancel_interval_nbr",
        readonly=False,
        store=True,
    )
    cancel_interval_unit = fields.Selection(
        CANCEL_INTERVAL_UNITS,
        string="Unit",
        compute="_compute_cancel_interval_unit",
        readonly=False,
        store=True,
    )

    @api.depends("event_type_id")
    def _compute_has_cancel(self):
        """Copy the setting from the template when it changes.

        Depends only on event_type_id, not on its sub fields, to emulate an
        onchange: editing the template must not touch existing events.
        """
        for event in self:
            if event.event_type_id:
                event.has_cancel = event.event_type_id.has_cancel
            else:
                event.has_cancel = True

    @api.depends("event_type_id")
    def _compute_cancel_interval_nbr(self):
        for event in self:
            if event.event_type_id:
                event.cancel_interval_nbr = event.event_type_id.cancel_interval_nbr
            else:
                event.cancel_interval_nbr = 1

    @api.depends("event_type_id")
    def _compute_cancel_interval_unit(self):
        for event in self:
            if event.event_type_id:
                event.cancel_interval_unit = event.event_type_id.cancel_interval_unit
            else:
                event.cancel_interval_unit = "days"
