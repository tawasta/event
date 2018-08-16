# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = 'event.event'

    # 2. Fields declaration
    show_track_twitter_hashtags = fields.Boolean(
        string='Show Twitter hashtag',
        help='Show Twitter hashtag in agenda',
    )

    overlapping_location_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping locations',
        compute='_compute_overlapping_location_track_ids',
    )

    overlapping_chairperson_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping chairpersons',
        compute='_compute_overlapping_chairperson_track_ids',
    )

    overlapping_speaker_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping speakers',
        compute='_compute_overlapping_speaker_track_ids',
    )

    # 3. Default methods
    @api.multi
    def name_get(self):
        # Override the name get to use only the event name as display name

        result = []
        for event in self:
            result.append((event.id, event.name))
        return result

    # 4. Compute and search fields
    @api.depends('track_ids')
    def _compute_overlapping_location_track_ids(self):
        for record in self:
            overlapping = list()

            for track in record.track_ids:
                overlapping += track.overlapping_location_track_ids.ids

            record.overlapping_location_track_ids = overlapping

    @api.depends('track_ids')
    def _compute_overlapping_chairperson_track_ids(self):
        for record in self:
            overlapping = list()

            for track in record.track_ids:
                overlapping += track.overlapping_chairperson_track_ids.ids

            record.overlapping_chairperson_track_ids = overlapping

    @api.depends('track_ids')
    def _compute_overlapping_speaker_track_ids(self):
        for record in self:
            overlapping = list()

            for track in record.track_ids:
                overlapping += track.overlapping_speaker_track_ids.ids

            record.overlapping_speaker_track_ids = overlapping

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
