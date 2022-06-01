##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
from werkzeug import urls

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):
    # 1. Private attribModelNameutes
    _inherit = "event.registration"

    # 2. Fields declaration
    registration_badge_url = fields.Char(
        "Registration Badge Download Link", compute="_compute_registration_badge_url"
    )
    registration_badge_downloaded = fields.Boolean(
        "Badge Downloaded", store=True, readonly=True
    )
    privacy_consent_ids = fields.One2many(
        comodel_name="privacy.consent",
        inverse_name="registration_ids",
        string="Privacy Consents",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_id", "access_token")
    def _compute_registration_badge_url(self):
        """Url to donwload registration badge"""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for registration in self:
            registration.registration_badge_url = urls.url_join(
                base_url,
                "/event/%s/registration/badge/%s"
                % (registration.event_id.id, registration.access_token),
            )

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
