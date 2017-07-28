# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackType(models.Model):
    # 1. Private attributes
    _name = 'event.track.type'

    # 2. Fields declaration
    name = fields.Char()
    description = fields.Text()
    active = fields.Boolean(
        default=True
    )

    event_tracks = fields.One2many(
        comodel_name='event.track',
        inverse_name='type',
        string='Event track',
    )

    # 3. Default methods

    # 4. Compute and search fields

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
