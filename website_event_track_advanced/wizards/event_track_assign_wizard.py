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
import random

# 3. Odoo imports (openerp):
from odoo import fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackAssignWizard(models.TransientModel):
    # 1. Private attributes
    _name = "event.track.assign.wizard"

    # 2. Fields declaration
    assign_random = fields.Boolean(
        string="Random assign", help="Randomize review groups", default=0
    )
    assign_equally = fields.Boolean(
        string="Assign equally",
        help='If un-checked, the assignation will use a "true" randomization. '
        "You probably do not want to use this, "
        "as it will most likely cause an unequal assignation.",
        default=1,
    )
    reassign_assigned = fields.Boolean(
        string="Reassign assigned",
        help="Assign the group even if the presentation already has " "a review group",
        default=1,
    )
    review_group = fields.Many2one(
        comodel_name="event.track.review.group", string="Review group"
    )
    track_ids = fields.Many2many(
        comodel_name="event.track",
        relation="assign_wizard_track",
        default=lambda self: self.env.context.get("active_ids"),
    )

    # 3. Default methods
    def default_get(self, fields):
        """ Get all unassigned tracks as default
        active_id = self._context['active_id']
        event = self.env['event.event'].browse([active_id])

        res['event_id'] = event.id
        res['track_ids'] = event.track_ids.search([
            ('event_id', '=', event.id),
            ('review_group', '=', False),
            ('state', 'in', ['confirmed']),
        ]).ids
        """
        res = super(EventTrackAssignWizard, self).default_get(fields)
        return res

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def action_assign_tracks(self):
        for wizard in self:
            track_ids = wizard._context.get("active_ids")
            if not track_ids:
                return
            EventTrack = self.env["event.track"]
            track_ids = EventTrack.browse(track_ids)
            if not self.reassign_assigned:
                # Don't reassign unless told to
                track_ids = track_ids.filtered(lambda r: r.review_group is False)
            # Random assignation
            if wizard.assign_random:
                wizard.randomize(track_ids, wizard.assign_equally)
                return True
            # Assign for one group
            track_ids.write(dict(review_group=wizard.review_group.id))

    # 8. Business methods
    def randomize(self, track_ids, equal=True):
        groups = self.env["event.track.review.group"].search([]).ids
        # Unequal assignation
        if not equal:
            for track in track_ids:
                track.review_group = random.choice(groups)
            return True
        # Equal assignation
        random.shuffle(groups)
        tracks = track_ids.ids
        random.shuffle(tracks)
        group_iterator = iter(groups)
        for track in tracks:
            try:
                next_track = group_iterator.__next__()
            except StopIteration:
                group_iterator = iter(groups)
                next_track = group_iterator.__next__()
            self.env["event.track"].browse([track]).review_group = next_track
        return True
