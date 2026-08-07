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
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventMailScheduler(models.Model):
    """Event automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on events since Odoo 9. A cron exists
    that periodically checks for mailing to run."""

    # 1. Private attributes
    _inherit = "event.mail"

    # 2. Fields declaration
    interval_type = fields.Selection(
        selection_add=[
            ("after_wait", "After registering to waiting list"),
            (
                "after_seats_available",
                "After more seats are available send to waiting list registrations",
            ),
        ],
        ondelete={"after_wait": "cascade", "after_seats_available": "cascade"},
    )

    # 8. Business methods
    def execute(self):
        """Keep this module's own interval types out of core's generic sweep.

        Core's own ``execute()`` has no branch for "after_wait" or
        "after_seats_available": they are not "after_sub" (attendee-based),
        and for a non-multi-slot event fall through to the generic "one
        shot, mail everyone" branch (``_execute_event_based()``, meant for
        before/after-event communication) - wrong for a per-registration
        mail that is already sent immediately and synchronously elsewhere
        (see ``EventEvent._compute_seats`` and ``EventRegistration.write``,
        both calling :meth:`_trigger_immediate_mail`). Left unfiltered, the
        periodic cron (``event.mail.schedule_communications``) would
        eventually pick these up too - typically once the event's
        ``date_end`` has passed, since their ``scheduled_date`` has no
        dedicated computation of its own and falls back to that - and mail
        the wrong recipients.
        """
        own_interval_types = ("after_wait", "after_seats_available")
        return super(
            EventMailScheduler,
            self.filtered(lambda s: s.interval_type not in own_interval_types),
        ).execute()

    def _trigger_immediate_mail(self, registrations):
        """Send each of these schedulers' mail to ``registrations`` right away.

        Loops over ``self`` rather than requiring a single scheduler, since
        callers filter ``event_mail_ids`` by ``interval_type`` and an event
        is free to have more than one scheduler of the same type (or none
        at all) - mirroring how core's own :meth:`_create_missing_mail_registrations`
        and :meth:`execute` handle a multi-record ``self`` on this same model.

        Unlike the cron-driven ``execute()``/``_execute_attendee_based()``
        flow, this also picks up ``event.mail.registration`` tracking rows
        that already exist but were reset (``mail_sent = False``) - e.g.
        when seats became unavailable again after a previous notification -
        not only brand new registrations. Both
        :meth:`_create_missing_mail_registrations` and
        :meth:`event.mail.registration._execute_on_registrations` are
        core methods, reused as-is.

        :param event.registration registrations: attendees to mail
        """
        if not registrations:
            return
        for scheduler in self:
            tracked = scheduler.mail_registration_ids.filtered(
                lambda mail_reg: mail_reg.registration_id in registrations
            )
            missing = registrations - tracked.registration_id
            if missing:
                tracked |= scheduler._create_missing_mail_registrations(missing)
            tracked.filtered(
                lambda mail_reg: not mail_reg.mail_sent
            )._execute_on_registrations()

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
