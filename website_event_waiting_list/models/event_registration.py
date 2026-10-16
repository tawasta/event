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
import uuid
from collections import defaultdict

from werkzeug.urls import url_join

from odoo import SUPERUSER_ID, api, fields, models, tools
from odoo.exceptions import ValidationError

# States that take a seat, like in core
SEAT_TAKING_STATES = ("open", "done")


class EventRegistration(models.Model):
    _inherit = "event.registration"

    waiting_list = fields.Boolean(related="event_id.waiting_list", store=True)
    waiting_list_to_confirm = fields.Boolean(
        string="Available to confirm from waiting list",
        readonly=True,
        compute_sudo=True,
        compute="_compute_waiting_list_to_confirm",
    )
    state = fields.Selection(
        selection_add=[("wait", "Waiting")], ondelete={"wait": "set draft"}
    )
    waiting_list_access_token = fields.Char(
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: str(uuid.uuid4()),
        help="Secret token identifying this registration in the public "
        "waiting-list confirm/cancel link, so that link works without the "
        "recipient needing to be logged in. Kept separate from any token "
        "other, independent modules may add for their own similar links.",
    )
    waiting_list_manage_url = fields.Char(
        string="Waiting List Manage Link",
        compute="_compute_waiting_list_manage_url",
    )

    def _auto_init(self):
        """Give every registration its own token.

        The ORM fills a newly created column with one default value evaluated
        once, so on a database that already has registrations they would all
        share the same token and each link would open every registration.
        """
        new_column = not tools.sql.column_exists(
            self.env.cr, self._table, "waiting_list_access_token"
        )
        res = super()._auto_init()
        if new_column:
            self.env.cr.execute(
                "UPDATE event_registration "
                "SET waiting_list_access_token = gen_random_uuid()::text"
            )
        return res

    @api.depends("event_id", "waiting_list_access_token")
    def _compute_waiting_list_manage_url(self):
        for registration in self:
            registration.waiting_list_manage_url = url_join(
                registration.get_base_url(),
                f"/event/{registration.event_id.id}/waiting-list/manage/"
                f"{registration.waiting_list_access_token}",
            )

    @api.depends(
        "state",
        "waiting_list",
        "event_slot_id",
        "event_ticket_id",
        "event_id.seats_available",
        "event_id.seats_limited",
        "event_id.seats_max",
        "event_id.kanban_state",
        "event_id.stage_id.pipe_end",
        "event_id.date_end",
        "event_slot_id.seats_available",
        "event_slot_id.end_datetime",
        "event_ticket_id.seats_available",
        "event_ticket_id.seats_max",
    )
    def _compute_waiting_list_to_confirm(self):
        """Whether this waiting registration can now be confirmed.

        True when the seats of its event (or slot) and ticket have no limit or a
        place left, and the event or slot is not cancelled or over. Core answers
        the limit question, so every way of limiting seats is covered.
        """
        self.waiting_list_to_confirm = False
        now = fields.Datetime.now()
        waiting = self.filtered(lambda r: r.state == "wait" and r.waiting_list)
        for event, registrations in waiting.grouped("event_id").items():
            if event._is_over():
                continue
            slot_tickets = list(
                {(r.event_slot_id, r.event_ticket_id) for r in registrations}
            )
            seats = dict(
                zip(
                    slot_tickets,
                    event._get_seats_availability(slot_tickets),
                    strict=True,
                )
            )
            for registration in registrations:
                slot = registration.event_slot_id
                available = seats[(slot, registration.event_ticket_id)]
                registration.waiting_list_to_confirm = (
                    not slot or slot.end_datetime >= now
                ) and (available is None or available > 0)

    @api.model_create_multi
    def create(self, vals_list):
        """Route the registrations that do not fit in the seats to the waiting list.

        ``state`` is set to ``"wait"`` in ``vals``, before ``super().create()``:
        core's own ``create()`` already mails the normal "you're registered" to
        any ``open`` registration, so moving it to ``wait`` afterwards is too late.
        """
        self._route_overflow_to_waiting_list(vals_list)
        registrations = super().create(vals_list)
        registrations.filtered(lambda r: r.state == "wait")._trigger_after_wait_mail()
        return registrations

    def write(self, vals):
        """Mail the registrations moved to the waiting list afterwards.

        One created straight into ``wait`` is handled by :meth:`create`. A seat
        may open up when the state or the archiving changes.
        """
        res = super().write(vals)
        if vals.get("state") == "wait":
            self._trigger_after_wait_mail()
        if vals.keys() & {"state", "active"}:
            self.event_id._trigger_mail_scheduler_cron()
        return res

    def unlink(self):
        events = self.event_id
        res = super().unlink()
        events._trigger_mail_scheduler_cron()
        return res

    def _route_overflow_to_waiting_list(self, vals_list):
        """Set ``state`` to ``wait`` for the registrations that find no seat.

        A batch is placed in the given order, so the first ones get the free seats
        and the rest wait. A seat has to be free in the event (or the slot) and in
        the ticket. Core answers whether it is (``_verify_seats_availability``),
        so every way of limiting seats is covered, and its check of the created
        registrations stays as a second guard.
        """
        # No state means the default one (open), or one computed from the order
        # (event_sale has no default), and both take a seat when confirmed
        seat_takers = [
            vals
            for vals in vals_list
            if vals.get("event_id")
            and vals.get("active", True)
            and vals.get("state", "open") in SEAT_TAKING_STATES
        ]
        events = (
            self.env["event.event"]
            .browse({vals["event_id"] for vals in seat_takers})
            .filtered("waiting_list")
        )
        events._lock_for_registration_changes()
        taken = defaultdict(int)
        for vals in seat_takers:
            if vals["event_id"] not in events.ids:
                continue
            event = events.browse(vals["event_id"])
            slot = self.env["event.slot"].browse(vals.get("event_slot_id"))
            ticket = self.env["event.event.ticket"].browse(vals.get("event_ticket_id"))
            keys = (event.id, slot.id), (event.id, slot.id, ticket.id)
            # A registration done already has its seat, but the others count on it
            if vals.get("state") != "done" and not self._has_free_seat(
                event, slot, ticket, taken[keys[0]] + 1, taken[keys[1]] + 1
            ):
                vals["state"] = "wait"
                continue
            for key in keys:
                taken[key] += 1

    def _has_free_seat(self, event, slot, ticket, event_count, ticket_count):
        """Whether the event (or slot) and the ticket have seats for these counts."""
        try:
            event._verify_seats_availability(
                [
                    (slot, self.env["event.event.ticket"], event_count),
                    (slot, ticket, ticket_count),
                ]
            )
        except ValidationError:
            return False
        return True

    def action_waiting(self):
        if not all(self.event_id.mapped("waiting_list")):
            raise ValidationError(
                self.env._("Waiting list for this event is not enabled.")
            )
        self.write({"state": "wait"})

    def action_waiting_confirm(self):
        """Confirm waiting registrations once a seat has actually opened up."""
        to_confirm = self.filtered(lambda r: r.state == "wait")
        to_confirm.event_id._lock_for_registration_changes()
        to_confirm.invalidate_recordset(["waiting_list_to_confirm"])
        for registration in to_confirm:
            if not registration.waiting_list_to_confirm:
                raise ValidationError(
                    self.env._(
                        "There are no seats available to confirm this registration yet."
                    )
                )
            registration.action_confirm()

    def action_waiting_cancel(self):
        """The attendee leaves the waiting list."""
        return self.action_cancel()

    def action_confirm(self):
        """Start the "after subscription" mails of the ones leaving the waiting list.

        Core does it only for registrations coming from draft or cancelled.
        """
        waiting = self.filtered(lambda r: r.state == "wait")
        res = super().action_confirm()
        waiting._update_mail_schedulers()
        return res

    def _trigger_after_wait_mail(self):
        """Send the "after_wait" mail right away to these registrations.

        Not for an event that is over or cancelled.
        """
        mailable = self.filtered(lambda r: not r.event_id._is_over())
        for event, registrations in mailable.grouped("event_id").items():
            schedulers = event.event_mail_ids.filtered(
                lambda s: s.interval_type == "after_wait"
            )
            # Like core runs the schedulers: the visitor who joins cannot read them
            schedulers.with_user(SUPERUSER_ID)._trigger_immediate_mail(registrations)
