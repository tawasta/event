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
from odoo.osv import expression

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        help="Enable waiting list when attendee limit is reached.",
        default=True,
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
                            "interval_type": "after_wait",
                            "template_id": self.env.ref(
                                "website_event_waiting_list.event_waiting"
                            ).id,
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
                                "website_event_waiting_list.event_confirm_waiting_registration"
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

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("seats_max", "registration_ids")
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
        base_vals = {fname: 0 for fname in state_field.values()}
        results = {event_id: dict(base_vals) for event_id in self.ids}
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

    @api.depends("event_type_id", "waiting_list")
    def _compute_waiting_list(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            event.waiting_list = event.event_type_id.waiting_list

    @api.depends(
        "date_tz",
        "start_sale_datetime",
        "date_end",
        "seats_available",
        "seats_limited",
        "event_ticket_ids.sale_available",
        "stage_id",
    )
    def _compute_event_registrations_open(self):
        """Compute whether people may take registrations for this event
        * event.date_end -> if event is done, registrations are not open anymore;
        * event.
        * event.start_sale_datetime -> lowest start date of tickets (if any; start_sale_datetime
          is False if no ticket are defined, see _compute_start_sale_datetime);
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
                    event.start_sale_datetime <= current_datetime.now()
                    if event.start_sale_datetime
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
                    or all(ticket.is_expired for ticket in event.event_ticket_ids)
                    else True
                )
                and not event.stage_id.cancel
            )

    # 5. Constraints and onchanges
    @api.constrains("seats_limited", "waiting_list")
    def _check_waiting_list(self):
        """Turn off waiting list if seats are not limited"""
        for event in self:
            if event.waiting_list and not event.seats_limited:
                event.waiting_list = False

    @api.constrains("seats_available", "waiting_list", "registration_ids")
    def _mail_to_waiting_list_confirmation(self):
        for event in self:
            if event.stage_id.pipe_end or event.stage_id.cancel:
                # Never try to send mail to closed events
                continue

            if event.waiting_list:
                # if seats are available, execute onsubscribe_schedulers
                if event.seats_available:
                    onsubscribe_schedulers = self.mapped("event_mail_ids").filtered(
                        lambda s: s.interval_type == "after_seats_available"
                    )
                    onsubscribe_schedulers.sudo().execute()
                # write "after_seats_available" mail as not sent
                # if seats become unavailable and mail was previously sent
                registrations_to_not_sent = self.mapped(
                    "event_mail_ids.mail_registration_ids"
                ).filtered(
                    lambda reg_mail: reg_mail.mail_sent
                    and reg_mail.registration_id.state == "wait"
                    and reg_mail.scheduler_id.notification_type == "mail"
                    and reg_mail.scheduler_id.interval_type == "after_seats_available"
                    and not reg_mail.registration_id.waiting_list_to_confirm
                )
                registrations_to_not_sent.write({"mail_sent": False})

    def _compute_is_participating(self):
        """Heuristic
        * public, no visitor: not participating as we have no information;
        * public and visitor: check visitor is linked to a registration. As
          visitors are merged on the top parent, current visitor check is
          sufficient even for successive visits;
        * logged, no visitor: check partner is linked to a registration. Do
          not check the email as it is not really secure;
        * logged as visitor: check partner or visitor are linked to a
          registration;
        """
        current_visitor = self.env["website.visitor"]._get_visitor_from_request(
            force_create=False
        )
        if self.env.user._is_public() and not current_visitor:
            events = self.env["event.event"]
        elif self.env.user._is_public():
            events = (
                self.env["event.registration"]
                .sudo()
                .search(
                    [
                        ("event_id", "in", self.ids),
                        ("state", "!=", "cancel"),
                        ("state", "!=", "wait"),
                        ("visitor_id", "=", current_visitor.id),
                    ]
                )
                .event_id
            )
        else:
            if current_visitor:
                domain = [
                    "|",
                    ("partner_id", "=", self.env.user.partner_id.id),
                    ("visitor_id", "=", current_visitor.id),
                ]
            else:
                domain = [("partner_id", "=", self.env.user.partner_id.id)]
            events = (
                self.env["event.registration"]
                .sudo()
                .search(
                    expression.AND(
                        [
                            domain,
                            [
                                "&",
                                ("event_id", "in", self.ids),
                                ("state", "!=", "cancel"),
                                ("state", "!=", "wait"),
                            ],
                        ]
                    )
                )
                .event_id
            )

        for event in self:
            event.is_participating = event in events

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def mail_attendees(
        self,
        template_id,
        force_send=False,
        filter_func=lambda self: self.state not in ["cancel", "wait", "draft"],
    ):
        for event in self:
            for attendee in event.registration_ids.filtered(filter_func):
                self.env["mail.template"].browse(template_id).send_mail(
                    attendee.id, force_send=force_send
                )

    # 8. Business methods
