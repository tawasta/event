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
import uuid

# 2. Known third party imports:
from werkzeug.urls import url_join

# 3. Odoo imports (openerp):
from odoo import api, fields, models
from odoo.exceptions import ValidationError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
    waiting_list = fields.Boolean(related="event_id.waiting_list", store=True)
    waiting_list_to_confirm = fields.Boolean(
        string="Available to confirm from waiting list",
        readonly=True,
        compute_sudo=True,
        compute="_compute_waiting_list_to_confirm",
    )
    state = fields.Selection(selection_add=[("wait", "Waiting")])
    waiting_list_access_token = fields.Char(
        readonly=True,
        copy=False,
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

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
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
        "event_id.seats_available",
        "event_id.seats_limited",
        "event_id.seats_max",
        "event_ticket_id.seats_available",
        "event_ticket_id.seats_limited",
        "event_ticket_id.seats_max",
    )
    def _compute_waiting_list_to_confirm(self):
        """Whether this waiting registration can now be confirmed.

        True when both the event and (if used) the ticket have either no
        seat limit, or a limit with at least one seat still available:

        1. Both ticket and event have limited but available seats
        2. Both ticket and event have no limited seats
        3. Ticket has no limited seats and event has limited but available seats
        4. Ticket has limited but available seats and event has no limited seats
        5. No ticket used and event has available seats
        """
        for registration in self:
            event = registration.event_id
            ticket = registration.event_ticket_id
            event_ok = (
                not event.seats_limited
                or not event.seats_max
                or (event.seats_available > 0)
            )
            ticket_ok = (
                not ticket
                or not ticket.seats_limited
                or not ticket.seats_max
                or (ticket.seats_available > 0)
            )
            registration.waiting_list_to_confirm = bool(
                registration.waiting_list
                and registration.state == "wait"
                and event_ok
                and ticket_ok
            )

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        """Route sold-out registrations straight into the waiting list.

        ``state`` is set to ``"wait"`` directly in ``vals``, before
        ``super().create()`` runs - not afterwards, through a follow-up
        :meth:`write` - because core's own ``create()`` calls
        ``_update_mail_schedulers()`` on the just-created records while
        still inside that same call (see core's
        ``event.registration.create()``), and that method fires the
        normal "you're registered" (``after_sub``) confirmation mail for
        any registration it finds in the ``open`` state - which every
        registration defaults to unless told otherwise. Leaving the
        ``state`` transition to a later ``write()`` therefore means the
        wrong confirmation mail has already gone out by the time this
        method would flip it to ``wait``, regardless of whether the
        waiting-list mail itself is configured correctly or not.

        Evaluated per record (not for the whole batch at once): a single
        sold-out ticket in a multi-registration submission must not push
        registrations for other, still-available tickets onto the waiting
        list too.
        """
        for vals in vals_list:
            if self._check_waiting_list(vals):
                vals["state"] = "wait"
        registrations = super().create(vals_list)
        registrations.filtered(lambda r: r.state == "wait")._trigger_after_wait_mail()
        return registrations

    def write(self, vals):
        """Trigger the "after_wait" mail scheduler(s) right after joining the waitlist.

        Only relevant for an existing registration moved to ``wait``
        afterwards (e.g. the "Move to Waiting List" backend action, via
        :meth:`action_waiting`) - a registration created straight into
        ``wait`` is already handled by :meth:`create` instead, since by
        the time this ``write()`` would run for it the mail has already
        been sent from there.
        """
        res = super().write(vals)
        if vals.get("state") == "wait":
            self._trigger_after_wait_mail()
        return res

    # 7. Action methods
    def action_waiting(self):
        if not self.event_id.waiting_list:
            raise ValidationError(
                self.env._("Waiting list for this event is not enabled.")
            )
        self.write({"state": "wait"})

    def action_waiting_confirm(self):
        """Confirm a waiting registration once a seat has actually opened up."""
        for registration in self:
            if registration.state != "wait":
                continue
            if not registration.waiting_list_to_confirm:
                raise ValidationError(
                    self.env._(
                        "There are no seats available to confirm this registration yet."
                    )
                )
            registration.action_confirm()

    def _check_waiting_list(self, vals):
        """Whether a registration being created with ``vals`` must wait.

        Must wait if *either* the event's own capacity or the selected
        ticket's capacity is exhausted, not only when both are - the event
        cap is a hard ceiling regardless of a specific ticket's own limit,
        and a ticket-less registration is only bound by the event cap.
        Mirrors :meth:`_compute_waiting_list_to_confirm`'s notion of
        "seats really available" (event_ok/ticket_ok), inverted and
        evaluated from raw ``vals`` since the registration does not exist
        yet at this point.

        :param dict vals: values passed to :meth:`create` for one registration
        :rtype: bool
        """
        if not vals.get("event_id"):
            return False

        event = self.env["event.event"].browse(vals["event_id"])
        if not event.waiting_list:
            return False

        ticket_id = vals.get("event_ticket_id")
        ticket = (
            self.env["event.event.ticket"].browse(ticket_id)
            if ticket_id
            else self.env["event.event.ticket"]
        )
        event_ok = (
            not event.seats_limited
            or not event.seats_max
            or (event.seats_available > 0)
        )
        ticket_ok = (
            not ticket
            or not ticket.seats_limited
            or not ticket.seats_max
            or (ticket.seats_available > 0)
        )
        return not (event_ok and ticket_ok)

    # 8. Business methods
    def _trigger_after_wait_mail(self):
        """Send the "after_wait" mail scheduler(s) immediately to these registrations.

        Shared by :meth:`create` (registration created straight into
        ``wait``) and :meth:`write` (an existing registration moved to
        ``wait`` afterwards) - both need the exact same immediate-mail
        trigger, just from a different moment in the registration's
        lifecycle. Skipped per-record for events whose stage is an end
        stage (``event.stage.pipe_end``) - closed events should not keep
        emailing attendees - without cutting the loop short for the rest
        of the batch.
        """
        for registration in self:
            if registration.event_id.stage_id.pipe_end:
                continue

            schedulers = registration.event_id.event_mail_ids.filtered(
                lambda s: s.interval_type == "after_wait"
            )
            schedulers.sudo()._trigger_immediate_mail(registration)
