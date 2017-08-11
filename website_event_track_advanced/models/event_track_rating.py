# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackRating(models.Model):
    # 1. Private attributes
    _name = 'event.track.rating'
    _rec_name = 'rating'

    # 2. Fields declaration
    event_track = fields.Many2one(
        comodel_name='event.track',
        string='Event track',
    )
    rating = fields.Integer(
        string='Rating',
    )
    comment = fields.Char(
        string='Comment',
    )

    # 3. Default methods

    # 4. Compute and search fields

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
