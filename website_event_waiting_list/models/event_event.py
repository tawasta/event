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
# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import api, fields, models
from odoo.exceptions import ValidationError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        help="Enable waiting list when attendee limit is reached.",
        tracking=True,
    )
    seats_waiting = fields.Integer(
        string="Seats on waiting list",
        readonly=True,
        compute="_compute_seats",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends(
        "event_slot_count",
        "is_multi_slots",
        "seats_max",
        "registration_ids.state",
        "registration_ids.active",
    )
    def _compute_seats(self):
        """Extend core seat computation to also count waiting-list seats.

        Also triggers the "seats available" mail scheduler(s) synchronously
        as soon as a compute of this event's seats reveals free capacity,
        and resets ``mail_sent`` on any not-yet-confirmed waiting attendee
        so that a seat becoming unavailable again does not leave them
        thinking they already got their confirmation email.
        """
        super()._compute_seats()

        for event in self:
            event.seats_waiting = 0

        base_vals = {"seats_waiting": 0}
        results = {event_id: dict(base_vals) for event_id in self.ids}

        if self.ids:
            query = """ SELECT event_id, count(event_id)
                        FROM event_registration
                        WHERE event_id IN %s AND state = 'wait' AND active = true
                        GROUP BY event_id
                    """
            self.env["event.registration"].flush_model(["event_id", "state", "active"])
            self.env.cr.execute(query, (tuple(self.ids),))
            for event_id, num in self.env.cr.fetchall():
                results[event_id]["seats_waiting"] = num

        for event in self:
            event.update(results.get(event._origin.id or event.id, base_vals))

            if event.waiting_list and event.seats_available > 0:
                event._trigger_seats_available_mails()

    def _trigger_seats_available_mails(self):
        """Send the "seats available" mail immediately to eligible waiting attendees.

        Also resets ``mail_sent`` for waiting attendees that were already
        notified but are no longer eligible (seats became unavailable
        again before they confirmed), so a future round of availability
        notifies them again instead of silently skipping them.
        """
        self.ensure_one()
        schedulers = self.event_mail_ids.filtered(
            lambda s: s.interval_type == "after_seats_available"
        )
        if schedulers:
            eligible = self.registration_ids.filtered(
                lambda r: r.state == "wait" and r.waiting_list_to_confirm
            )
            schedulers.sudo()._trigger_immediate_mail(eligible)

        stale_mail_registrations = self.event_mail_ids.mapped(
            "mail_registration_ids"
        ).filtered(
            lambda reg_mail: reg_mail.mail_sent
            and reg_mail.registration_id.state == "wait"
            and reg_mail.scheduler_id.interval_type == "after_seats_available"
            and not reg_mail.registration_id.waiting_list_to_confirm
        )
        stale_mail_registrations.write({"mail_sent": False})

    def _verify_seats_availability(self, slot_tickets):
        """Skip the hard seat-overflow block for the website registration flow.

        When this event has a waiting list, an overflowing website
        submission should be routed to the waiting list by
        :meth:`event.registration.create`, not rejected outright. Scoped
        via context to that one flow (see
        ``WebsiteEventControllerWaiting.registration_confirm``), not a
        blanket bypass, so normal overselling protection still applies
        everywhere else (manually confirming waiting attendees, backend
        edits, ...).
        """
        self.ensure_one()
        if self.waiting_list and self.env.context.get(
            "website_event_waiting_list_bypass_seats_check"
        ):
            return
        return super()._verify_seats_availability(slot_tickets)

    @api.onchange("event_type_id")
    def _onchange_event_type_update_wait_list(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its subfields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if event.event_type_id:
                event.waiting_list = event.event_type_id.waiting_list

    # 5. Constraints and onchanges
    @api.constrains("seats_limited", "waiting_list")
    def _check_waiting_list(self):
        """Turn off waiting list if seats are not limited"""
        for event in self:
            if event.waiting_list and not event.seats_limited:
                event.waiting_list = False

    @api.constrains("seats_max", "seats_limited", "registration_ids")
    def _check_seats_availability(self, minimal_availability=0):
        sold_out_events = []
        for event in self:
            if (
                not event.waiting_list
                and event.seats_limited
                and event.seats_max
                and event.seats_available < minimal_availability
            ):
                sold_out_events.append(
                    self.env._(
                        '- "%(event_name)s": Missing %(nb_too_many)i seats.',
                        event_name=event.name,
                        nb_too_many=-event.seats_available,
                    )
                )
        if sold_out_events:
            raise ValidationError(
                self.env._("There are not enough seats available for:")
                + "\n%s\n" % "\n".join(sold_out_events)
            )

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
