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

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    privacy_ids = fields.Many2many("privacy.activity", string="Privacies")


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    privacy_ids = fields.Many2many(
        "privacy.activity",
        string="Privacies",
        readonly=False,
        store=True,
        compute="_compute_privacy_ids",
        default=lambda self: self.env["privacy.activity"]
        .sudo()
        .search([("show_in_event", "=", True)])
        .ids,
    )
    create_partner = fields.Boolean(
        compute="_compute_create_partner", store=True, readonly=False
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("privacy_ids")
    def _compute_create_partner(self):
        """A consent needs a partner, so the registrations of an event that asks
        for consents always create their partner."""
        for event in self:
            if event.privacy_ids:
                event.create_partner = True

    @api.depends("event_type_id")
    def _compute_privacy_ids(self):
        """Copy privacies from the event type once, like an onchange.

        Only runs when the event has none yet, so editing the event's own
        ``privacy_ids`` afterwards is not overwritten by a later
        ``event_type_id`` recompute trigger.
        """
        for event in self:
            if not event.privacy_ids and event.event_type_id.privacy_ids:
                event.privacy_ids = event.event_type_id.privacy_ids

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        """Enable the partner creation of an event created with privacies.

        ``partner_event`` gives ``create_partner`` a default value, and the
        form does not post the field while it is readonly, so on create the
        default wins and the compute does not run.
        """
        events = super().create(vals_list)
        events.filtered(
            lambda event: event.privacy_ids and not event.create_partner
        ).create_partner = True
        return events

    # 7. Action methods

    # 8. Business methods
