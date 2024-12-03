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


# 3. Odoo imports (openerp):
from odoo import fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    show_date_time = fields.Boolean(
        string="Näytä päivämäärä ja aika",
        default=True,
        help="Jos tämä valitaan, tapahtuman päivämäärä ja aika näytetään frontendissä.",
    )
    show_location = fields.Boolean(
        string="Näytä sijainti",
        default=True,
        help="Jos tämä valitaan, tapahtuman sijainti näytetään frontendissä.",
    )
    show_share = fields.Boolean(
        string="Näytä jako",
        default=True,
        help="Jos tämä valitaan, tapahtuman jako näytetään frontendissä.",
    )

    # 8. Business methods
