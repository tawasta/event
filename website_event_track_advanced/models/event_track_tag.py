# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackTag(models.Model):
    # 1. Private attributes
    _inherit = 'event.track.tag'

    # 2. Fields declaration
    tracks = fields.Many2many(
        comodel_name='event.track',
        string='Tracks',
    )
    track_count = fields.Integer(
        string='Track count',
        compute='compute_track_count',
        store=True,
    )

    # 3. Default methods

    # 4. Compute and search fields
    @api.depends('tracks')
    def compute_track_count(self):
        for record in self:
            record.track_count = len(record.tracks)

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
