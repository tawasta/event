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
from odoo import models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def _create_privacy(self, privacy_vals, partner, event):
        """Create or update ``partner``'s consent for each of ``event``'s privacies.

        :param dict privacy_vals: posted ``privacy_<activity_id>`` checkbox
            values, keyed like the checkbox names in the registration form
        :param res.partner partner: partner the consent is recorded for
        :param event.event event: event whose ``privacy_ids`` are being answered
        """
        for activity in event.privacy_ids:
            accepted = bool(privacy_vals.get(f"privacy_{activity.id}"))
            consent = (
                self.env["privacy.consent"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", partner.id),
                        ("activity_id", "=", activity.id),
                    ]
                )
            )
            if consent:
                consent.write({"accepted": accepted})
            else:
                self.env["privacy.consent"].sudo().create(
                    {
                        "partner_id": partner.id,
                        "activity_id": activity.id,
                        "accepted": accepted,
                        "state": "answered",
                    }
                )

    # 8. Business methods
