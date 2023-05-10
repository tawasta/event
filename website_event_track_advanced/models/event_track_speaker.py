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

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackSpeaker(models.Model):
    # 1. Private attributes
    _name = "event.track.speaker"
    _order = "sequence"


    def _default_sequence(self):
        return (self.search([], order="sequence desc", limit=1).sequence or 0) + 1

    # 2. Fields declaration
    track_id = fields.Many2one(comodel_name="event.track", string="Track")

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")

    email = fields.Char(related="partner_id.email")

    phone = fields.Char(related="partner_id.phone")

    sequence = fields.Integer(string="Sequence", default=_default_sequence)

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
