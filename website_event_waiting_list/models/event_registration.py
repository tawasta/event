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
        string="Waiting List Access Token",
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
            event_ok = not event.seats_limited or not event.seats_max or (
                event.seats_available > 0
            )
            ticket_ok = not ticket or not ticket.seats_limited or not ticket.seats_max or (
                ticket.seats_available > 0
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
        """Move newly created registrations to the waiting list where needed.

        Evaluated per record (not for the whole batch at once): a single
        sold-out ticket in a multi-registration submission must not push
        registrations for other, still-available tickets onto the waiting
        list too.
        """
        registrations = super().create(vals_list)
        waiting_registration_ids = [
            registration.id
            for registration, vals in zip(registrations, vals_list, strict=True)
            if self._check_waiting_list(vals)
        ]
        if waiting_registration_ids:
            self.browse(waiting_registration_ids).sudo().action_waiting()
        return registrations

    def write(self, vals):
        """Trigger the "after_wait" mail scheduler(s) right after joining the waitlist.

        ``after_sub`` scheduling on confirmation is already handled by core's
        own ``write()`` (see ``_update_mail_schedulers``); only the new
        waiting-list trigger needs to be added here. Skipped per-record for
        events whose stage is closed or cancelled - closed events should not
        keep emailing attendees - without cutting the loop short for the
        rest of the batch.
        """
        res = super().write(vals)

        if vals.get("state") != "wait":
            return res

        for registration in self:
            event_stage = registration.event_id.stage_id
            if event_stage.pipe_end or event_stage.cancel:
                continue

            schedulers = registration.event_id.event_mail_ids.filtered(
                lambda s: s.interval_type == "after_wait"
            )
            schedulers.sudo()._trigger_immediate_mail(registration)

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
                        "There are no seats available to confirm this "
                        "registration yet."
                    )
                )
            registration.action_confirm()

    def _check_waiting_list(self, vals):
        """Whether a registration being created with ``vals`` must wait.

        :param dict vals: values passed to :meth:`create` for one registration
        :rtype: bool
        """
        if not vals.get("event_id") or not vals.get("event_ticket_id"):
            return False

        event = self.env["event.event"].browse(vals["event_id"])
        ticket = self.env["event.event.ticket"].browse(vals.get("event_ticket_id"))

        return bool(
            event.waiting_list
            and event.seats_limited
            and event.seats_available <= 0
            and ticket.seats_limited
            and ticket.seats_available <= 0
        )

    # 8. Business methods
