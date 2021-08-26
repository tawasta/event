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

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    registration_elsewhere = fields.Boolean(
        "Registration Elsewhere",
        help="Selecting this option disables registration through the system "
        "and redirects registrations to an external link.",
        readonly=False,
        store=True,
    )
    registration_link = fields.Char(
        "Registration Link (URL)",
        help="Enter the URL address of an external registration link.",
        readonly=False,
        store=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    registration_elsewhere = fields.Boolean(
        "Registration Elsewhere",
        help="Selecting this option disables registration through the system "
        "and redirects registrations to an external link.",
        readonly=False,
        store=True,
        compute="_compute_registration_elsewhere",
    )
    registration_link = fields.Char(
        "Registration Link (URL)",
        help="Enter the URL address of an external registration link.",
        readonly=False,
        store=True,
        compute="_compute_registration_link",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_type_id")
    def _compute_registration_elsewhere(self):
        """ Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method. """
        for event in self:
            if (
                event.event_type_id.registration_elsewhere
                != event.registration_elsewhere
            ):
                event.registration_elsewhere = (
                    event.event_type_id.registration_elsewhere
                )
            if not event.registration_elsewhere:
                event.registration_elsewhere = False

    @api.depends("event_type_id")
    def _compute_registration_link(self):
        """ Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method. """
        for event in self:
            if not event.event_type_id:
                event.registration_link = event.registration_link or None
            else:
                event.registration_link = event.event_type_id.registration_link or None

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
