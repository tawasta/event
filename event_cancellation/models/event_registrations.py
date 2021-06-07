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
import uuid
from datetime import datetime
import pytz

# 2. Known third party imports:
from werkzeug import urls

# 3. Odoo imports (openerp):
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
    manage_url = fields.Char("Public link", compute="_compute_manage_url")
    access_token = fields.Char(
        "Security Token", store=True, compute="_compute_access_token"
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_id", "access_token")
    def _compute_manage_url(self):
        """ Url to cancel registration """
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for registration in self:
            registration.manage_url = urls.url_join(
                base_url,
                "/event/%s/registration/manage/%s"
                % (registration.event_id.id, registration.access_token),
            )

    def _compute_access_token(self):
        for registration in self:
            registration.access_token = str(uuid.uuid4())

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to assign write access_token.
        """
        self = self.with_context(skip_confirm=True)
        registrations = super(EventRegistration, self).create(vals_list)
        registrations = registrations.with_context(skip_confirm=False)
        for registration in registrations:
            if not registration.access_token:
                registration.sudo().write({"access_token": str(uuid.uuid4())})
        if registrations._check_auto_confirmation():
            registrations.sudo().action_confirm()
        return registrations

    # 7. Action methods
    def action_cancel(self):
        if not self.event_id.able_to_cancel:
            raise ValidationError(
                _(
                    "Can not cancel registration after %s"
                    % self.event_id.cancel_before_date.astimezone(
                        pytz.timezone(self.event_id.date_tz or "UTC")
                    )
                )
            )
        self.write({"state": "cancel"})

    def _check_auto_confirmation(self):
        if self._context.get("skip_confirm"):
            return False
        if any(
            not registration.event_id.auto_confirm
            or (
                not registration.event_id.seats_available
                and registration.event_id.seats_limited
            )
            for registration in self
        ):
            return False
        return True

    # 8. Business methods
