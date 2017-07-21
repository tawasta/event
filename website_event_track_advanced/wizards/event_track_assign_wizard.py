# -*- coding: utf-8 -*-

# 1. Standard library imports:
import random

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackAssignWizard(models.TransientModel):
    # 1. Private attributes
    _name = 'event.track.assign.wizard'

    # 2. Fields declaration
    assign_equally = fields.Boolean(
        string='Assign equally',
        help='If un-checked, the assignation will use a "true" randomization'
        + 'You probably do not want to use this, as it will most likely cause an unequal assignation.',
        default=1,
    )

    event_id = fields.Many2one(
        comodel_name='event.event',
        string='Event',
    )
    track_ids = fields.One2many(
        comodel_name='event.track',
        inverse_name='event_id',
    )

    # 3. Default methods
    @api.model
    def default_get(self, fields):
        res = super(EventTrackAssignWizard, self).default_get(fields)

        active_id = self._context['active_id']
        event = self.env['event.event'].browse([active_id])

        res['event_id'] = event.id
        res['track_ids'] = event.track_ids.search([
            ('event_id', '=', event.id),
            ('review_group', '=', False),
            ('state', 'in', ['draft']),
        ]).ids

        return res

    # 4. Compute and search fields

    # 5. Constraints and onchanges
    @api.onchange('assign_equally')
    def onchange_assign_equally_do_randomize(self):
        self.randomize(self.assign_equally)

    # 6. CRUD methods

    # 7. Action methods

    def action_assign_tracks(self):
        pass

    # 8. Business methods
    def randomize(self, equal=True):
        groups = self.env['event.track.review.group'].search([]).ids

        # Unequal assignation
        if not equal:
            for track in self.track_ids:
                track.review_group = random.choice(groups)
            return True

        # Equal assignation
        random.shuffle(groups)

        tracks = self.track_ids.ids
        random.shuffle(tracks)

        group_iterator = iter(groups)

        for track in tracks:
            try:
                next = group_iterator.next()
            except StopIteration:
                group_iterator = iter(groups)
                next = group_iterator.next()

            self.env['event.track'].browse([track]).review_group = next

        return True
