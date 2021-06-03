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
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models, api

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_INTERVALS = {
    "hours": lambda interval: relativedelta(hours=interval),
    "days": lambda interval: relativedelta(days=interval),
    "weeks": lambda interval: relativedelta(days=7 * interval),
}


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        help="Enable waiting list when attendee limit is reached.",
        default=True,
    )
    cancel_interval_nbr = fields.Integer("Interval", default=1)
    cancel_interval_unit = fields.Selection(
        [("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")],
        string="Unit",
        default="hours",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("use_mail_schedule")
    def _compute_event_type_mail_ids(self):
        for template in self:
            if not template.use_mail_schedule:
                template.event_type_mail_ids = [(5, 0)]
            elif not template.event_type_mail_ids:
                template.event_type_mail_ids = [
                    (
                        0,
                        0,
                        {
                            "notification_type": "mail",
                            "interval_unit": "now",
                            "interval_type": "after_sub",
                            "template_id": self.env.ref("event.event_subscription").id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "notification_type": "mail",
                            "interval_unit": "now",
                            "interval_type": "after_wait",
                            "template_id": self.env.ref(
                                "event_waiting_list.event_waiting"
                            ).id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "notification_type": "mail",
                            "interval_nbr": 10,
                            "interval_unit": "days",
                            "interval_type": "before_event",
                            "template_id": self.env.ref("event.event_reminder").id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "notification_type": "mail",
                            "interval_unit": "now",
                            "interval_type": "after_seats_available",
                            "template_id": self.env.ref(
                                "event_waiting_list.event_confirm_waiting_registration"
                            ).id,
                        },
                    ),
                ]

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        compute="_compute_waiting_list",
        help="Enable waiting list when attendee limit is reached.",
        readonly=False,
        store=True,
    )
    seats_waiting = fields.Integer(
        string="Seats on waiting list",
        store=True,
        readonly=True,
        compute="_compute_seats",
    )
    cancel_interval_nbr = fields.Integer(
        string="Interval",
        compute="_compute_cancel_interval_nbr",
        required=True,
        readonly=False,
        store=True,
    )
    cancel_interval_unit = fields.Selection(
        [("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")],
        string="Unit",
        required=True,
        compute="_compute_cancel_interval_unit",
        readonly=False,
        store=True,
    )
    cancel_before_date = fields.Datetime(
        "Cancel before date", compute="_compute_before_date", store=True
    )
    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
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

    @api.depends("cancel_interval_unit", "cancel_interval_nbr")
    def _compute_before_date(self):
        for event in self:
            date, sign = event.date_begin, -1
            event.cancel_before_date = (
                date
                + _INTERVALS[event.cancel_interval_unit](
                    sign * event.cancel_interval_nbr
                )
                if date
                else False
            )

    @api.depends("seats_max", "registration_ids.state")
    def _compute_seats(self):
        """
        Determine reserved, available, reserved but unconfirmed,
        used and waiting seats.
        """
        # initialize fields to 0
        for event in self:
            event.seats_unconfirmed = (
                event.seats_reserved
            ) = event.seats_used = event.seats_available = event.seats_waiting = 0
        # aggregate registrations by event and by state
        state_field = {
            "draft": "seats_unconfirmed",
            "open": "seats_reserved",
            "done": "seats_used",
            "wait": "seats_waiting",
        }
        base_vals = dict((fname, 0) for fname in state_field.values())
        results = dict((event_id, dict(base_vals)) for event_id in self.ids)
        if self.ids:
            query = """ SELECT event_id, state, count(event_id)
                        FROM event_registration
                        WHERE event_id IN %s AND state IN ('draft', 'open', 'done', 'wait')
                        GROUP BY event_id, state
                        """
            self.env["event.registration"].flush(["event_id", "state"])
            self._cr.execute(query, (tuple(self.ids),))
            res = self._cr.fetchall()
            for event_id, state, num in res:
                results[event_id][state_field[state]] += num

        # compute seats_available and send automatic mail to waiting list
        # if waiting list enabled and more seats become available
        for event in self:
            event.update(results.get(event._origin.id or event.id, base_vals))
            if event.seats_max > 0:
                event.seats_available = event.seats_max - (
                    event.seats_reserved + event.seats_used
                )
                # write "after_seats_available" mail as not sent
                # if seats become unavailable
                todo = self.mapped("event_mail_ids.mail_registration_ids").filtered(
                    lambda reg_mail: reg_mail.mail_sent
                    and reg_mail.registration_id.state == "wait"
                    and reg_mail.scheduler_id.notification_type == "mail"
                    and reg_mail.scheduler_id.interval_type == "after_seats_available"
                    and reg_mail.mail_sent
                    and not reg_mail.registration_id.waiting_list_to_confirm
                )
                todo.write({"mail_sent": False})

                # try to send "after_seats_available" mail to waiting_list
                # validation is done once more in execute
                onsubscribe_schedulers = self.mapped("event_mail_ids").filtered(
                    lambda s: s.interval_type == "after_seats_available"
                )
                onsubscribe_schedulers.sudo().execute()

    @api.depends("event_type_id", "waiting_list")
    def _compute_waiting_list(self):
        """ Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method. """
        for event in self:
            event.waiting_list = event.event_type_id.waiting_list

    @api.depends(
        "date_tz",
        "start_sale_date",
        "date_end",
        "seats_available",
        "seats_limited",
        "event_ticket_ids.sale_available",
    )
    def _compute_event_registrations_open(self):
        """ Compute whether people may take registrations for this event
          * event.date_end -> if event is done, registrations are not open anymore;
          * event.
          * event.start_sale_date -> lowest start date of tickets (if any; start_sale_date
            is False if no ticket are defined, see _compute_start_sale_date);
          * any ticket is available for sale (seats available) if any;
          * seats are unlimited or seats are available;
          * allow registrations to waiting list if enabled
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
                    event.start_sale_date <= current_datetime.date()
                    if event.start_sale_date
                    else True
                )
                and (date_end_tz >= current_datetime if date_end_tz else True)
                and (
                    not event.seats_limited or event.seats_available
                    if not event.waiting_list
                    else True
                )
                and (
                    not event.event_ticket_ids
                    or any(ticket.sale_available for ticket in event.event_ticket_ids)
                    if not event.waiting_list
                    else True
                )
            )

    # 5. Constraints and onchanges
    @api.constrains("seats_limited", "waiting_list")
    def _check_waiting_list(self):
        """ Turn off waiting list if seats are not limited """
        for event in self:
            if event.waiting_list and not event.seats_limited:
                event.waiting_list = False

    # 6. CRUD methods

    # 7. Action methods
    def mail_attendees(
        self,
        template_id,
        force_send=False,
        filter_func=lambda self: self.state not in ["cancel", "wait"],
    ):
        for event in self:
            for attendee in event.registration_ids.filtered(filter_func):
                self.env["mail.template"].browse(template_id).send_mail(
                    attendee.id, force_send=force_send
                )

    # 8. Business methods
