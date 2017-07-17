# -*- coding: utf-8 -*-

# 1. Standard library imports:
import difflib

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackTargetGroup(models.Model):
    # 1. Private attributes
    _name = 'event.track.target.group'

    # 2. Fields declaration
    name = fields.Char(
        string='Target group',
    )
    event_track = fields.Many2many(
        comodel_name='event.track',
        relation='target_group',
        string='Event track',
    )

    # 3. Default methods

    # 4. Compute and search fields

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
