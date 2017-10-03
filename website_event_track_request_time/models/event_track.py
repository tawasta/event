# -*- coding: utf-8 -*-

# 1. Standard library imports:
import difflib

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models
from odoo import _
from odoo.tools import html2plaintext
from odoo.exceptions import AccessError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrack(models.Model):
    # 1. Private attributes
    _inherit = 'event.track'

    # 2. Fields declaration
    request_time = fields.Many2one(
        comodel_name='event.track.request.time',
        string='Request time',
    )

    # 3. Default methods

    # 4. Compute and search fields

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
