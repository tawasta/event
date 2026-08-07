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
    def _default_event_mail_type_ids_with_waiting_list(self):
        """Extend core's own event-type mail-schedule defaults.

        Core's ``event_type_mail_ids`` field stores a direct reference to
        ``_default_event_mail_type_ids`` as its ``default=`` (not a method
        name string), so simply overriding that method here would never
        actually run: Odoo calls the stored function reference directly,
        bypassing the override. The field is therefore redeclared below
        with a new default that calls into core's own method through
        ``self`` (which *does* go through the normal override chain) and
        appends the waiting-list schedulers. The field's own ``default=``
        below wraps this method in a ``lambda self: ...`` for the same
        reason, rather than repeating core's mistake here: a bare
        function reference would stop any *further* module from being
        able to override this method either.
        """
        return self._default_event_mail_type_ids() + [
            (
                0,
                0,
                {
                    "interval_nbr": 0,
                    "interval_unit": "now",
                    "interval_type": "after_wait",
                    "template_ref": "mail.template,{}".format(
                        self.env.ref("website_event_waiting_list.event_waiting").id
                    ),
                },
            ),
            (
                0,
                0,
                {
                    "interval_nbr": 0,
                    "interval_unit": "now",
                    "interval_type": "after_seats_available",
                    "template_ref": "mail.template,{}".format(
                        self.env.ref(
                            "website_event_waiting_list."
                            "event_confirm_waiting_registration"
                        ).id
                    ),
                },
            ),
        ]

    event_type_mail_ids = fields.One2many(
        "event.type.mail",
        "event_type_id",
        string="Mail Schedule",
        default=lambda self: self._default_event_mail_type_ids_with_waiting_list(),
    )

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
