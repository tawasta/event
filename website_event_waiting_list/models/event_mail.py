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

        Core's ``execute()`` has no branch for "after_wait"/
        "after_seats_available" and would fall through to its "mail
        everyone" one-shot branch - wrong for a per-registration mail
        already sent immediately elsewhere (see :meth:`_trigger_immediate_mail`).
        """
        own_interval_types = ("after_wait", "after_seats_available")
        return super(
            EventMailScheduler,
            self.filtered(lambda s: s.interval_type not in own_interval_types),
        ).execute()

    def _trigger_immediate_mail(self, registrations):
        """Send each of these schedulers' mail to ``registrations`` right away.

        Loops over ``self`` instead of requiring a single scheduler, since
        an event can have zero or several of the same ``interval_type``.
        Also re-sends to a registration whose ``mail_sent`` was reset (e.g.
        seats became unavailable again), not only to brand new ones.
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
