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

import logging

# 3. Odoo imports (openerp):
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    banner_image = fields.Image(
        "Banner Image",
        readonly=False,
        store=True,
        max_width=1920,
        max_height=1080,
        verify_resolution=True,
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
    banner_image = fields.Image(
        "Banner Image",
        readonly=False,
        store=True,
        max_width=1920,
        max_height=1080,
        verify_resolution=True,
        compute="_compute_banner_image",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_type_id")
    def _compute_banner_image(self):
        """Set banner image from event type."""
        for event in self:
            if not event.event_type_id:
                event.banner_image = event.banner_image or None
            else:
                event.banner_image = event.event_type_id.banner_image or None

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
