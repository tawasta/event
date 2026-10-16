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

BYPASS_SEATS_CHECK_CONTEXT_KEY = "website_event_waiting_list_bypass_seats_check"


class EventEvent(models.Model):
    _inherit = "event.event"

    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        compute="_compute_waiting_list",
        readonly=False,
        store=True,
        precompute=True,
        tracking=True,
        help="Enable waiting list when attendee limit is reached.",
    )
    seats_waiting = fields.Integer(
        string="Seats on waiting list",
        compute="_compute_seats_waiting",
        compute_sudo=True,
    )
    waiting_list_open = fields.Boolean(
        string="Open for the waiting list",
        compute="_compute_waiting_list_open",
        compute_sudo=True,
        help="Everything is sold out, so a registration joins the waiting list.",
    )

    @api.depends("event_type_id")
    def _compute_waiting_list(self):
        """Copy the setting from the template when it changes, not when it is edited."""
        for event in self:
            event.waiting_list = (event.event_type_id or event).waiting_list

    @api.depends("registration_ids.state", "registration_ids.active")
    def _compute_seats_waiting(self):
        waiting = dict(
            self.env["event.registration"]._read_group(
                [("event_id", "in", self.ids), ("state", "=", "wait")],
                ["event_id"],
                ["__count"],
            )
        )
        for event in self:
            event.seats_waiting = waiting.get(event._origin, 0)

    @api.depends(
        "waiting_list", "event_registrations_open", "event_registrations_sold_out"
    )
    def _compute_waiting_list_open(self):
        for event in self:
            event.waiting_list_open = (
                event.waiting_list
                and event.event_registrations_open
                and event.event_registrations_sold_out
            )

    @api.depends("waiting_list", "kanban_state", "event_registrations_sold_out")
    def _compute_event_registrations_open(self):
        """Registrations stay open for the waiting list when everything is sold out."""
        res = super()._compute_event_registrations_open()
        for event in self:
            if event.waiting_list and not event.event_registrations_open:
                event.event_registrations_open = event._is_waiting_list_joinable()
        return res

    def _get_waiting_list_order_limit(self, ticket=None):
        """Most tickets of one kind that an order for the waiting list can have.

        More than the seats of the event (or slot) or of the ticket could never be
        confirmed, so the order is capped by them, and by the limit per order of
        the ticket. The seats left do not count: the ones that do not fit wait.
        """
        self.ensure_one()
        ticket = ticket or self.env["event.event.ticket"]
        limits = [self.EVENT_MAX_TICKETS, ticket.limit_max_per_order]
        if self.seats_limited:
            limits.append(self.seats_max)
        if ticket.seats_limited:
            limits.append(ticket.seats_max)
        return min(limit for limit in limits if limit > 0)

    def _is_over(self):
        """Whether the event is cancelled, in an end stage or past its end."""
        self.ensure_one()
        return bool(
            self.kanban_state == "cancel"
            or self.stage_id.pipe_end
            or (self.date_end and self.date_end < fields.Datetime.now())
        )

    def _is_waiting_list_joinable(self):
        """Whether the only thing keeping registrations closed is that all is sold out.

        A cancelled or ended event, or one whose tickets are not on sale, has
        no waiting list either.
        """
        self.ensure_one()
        return bool(
            self.event_registrations_sold_out
            and self.event_registrations_started
            and (not self.is_multi_slots or self.event_slot_count)
            and not self._is_over()
            and (
                not self.event_ticket_ids
                or any(
                    t.is_launched and not t.is_expired for t in self.event_ticket_ids
                )
            )
        )

    def _lock_for_registration_changes(self):
        """Serialize concurrent changes of the seats of these events.

        Two visitors who take the last seat at the same moment would both see it
        free, as the check of core locks nothing. A lock alone is not enough:
        transactions work on a snapshot (repeatable read), so after the wait the
        second would still count the seats of its old snapshot. The row is also
        updated, which makes the second fail with a serialization error once the
        first has committed. The request is run again and sees the seat taken.
        """
        if not self:
            return
        self.env.cr.execute(
            """
            UPDATE event_event SET write_date = write_date
             WHERE id IN (SELECT id FROM event_event WHERE id IN %s
                           ORDER BY id FOR UPDATE)
            """,
            (tuple(self.ids),),
        )
        self.env.invalidate_all()

    def _verify_seats_availability(self, slot_tickets):
        """Skip the seat-overflow block for the website registration of this module.

        An overflowing submission should become a waiting registration, not be
        rejected. Only the check of ``registration_confirm`` carries the flag: the
        registrations are created without it, so the check of core still guards
        them, and the ones over the limit are created as waiting.
        """
        self.ensure_one()
        if self.waiting_list and self.env.context.get(BYPASS_SEATS_CHECK_CONTEXT_KEY):
            return
        return super()._verify_seats_availability(slot_tickets)

    @api.model_create_multi
    def create(self, vals_list):
        """Make sure a waiting-list event has its mail schedulers.

        Checked on the created records, not ``vals_list``, as ``waiting_list``
        can be true without a key (copied from the template).
        """
        events = super().create(vals_list)
        events.filtered("waiting_list")._ensure_waiting_list_mail_schedulers()
        return events

    def write(self, vals):
        """Check the schedulers when the waiting list or the template changes.

        More seats may have opened up if the limit changed.
        """
        res = super().write(vals)
        if vals.keys() & {"waiting_list", "event_type_id"}:
            self.filtered("waiting_list")._ensure_waiting_list_mail_schedulers()
        if vals.keys() & {"waiting_list", "seats_limited", "seats_max"}:
            self._trigger_mail_scheduler_cron()
        return res

    def _trigger_mail_scheduler_cron(self):
        """Run the mail schedulers soon, as core does when something changes.

        The cron of core runs the scheduler of the free seats only every 24
        hours, so it is asked to run now when a seat may have opened up.
        """
        self.env.ref("event.event_mail_scheduler")._trigger()

    def _ensure_waiting_list_mail_schedulers(self):
        """Create the waiting-list schedulers an event is missing.

        One that already exists (by ``interval_type``) is left alone, so a
        customised scheduler stays.
        """
        templates = self.env["event.mail"]._get_waiting_list_templates()
        vals_list = [
            {
                "event_id": event.id,
                "interval_nbr": 0,
                "interval_unit": "now",
                "interval_type": interval_type,
                "template_ref": f"mail.template,{template.id}",
            }
            for event in self
            for interval_type, template in templates.items()
            if interval_type not in event.event_mail_ids.mapped("interval_type")
        ]
        if vals_list:
            # sudo: whoever saves the event may not have the right to the schedulers
            self.env["event.mail"].sudo().create(vals_list)
