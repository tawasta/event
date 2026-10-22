##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
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
from odoo import models


class EventEvent(models.Model):
    _inherit = "event.event"

    def write(self, vals):
        """Keep the publishing and the published stage together.

        An event that is published moves to the first published stage, and an
        event that moves to a published stage is published. Each step leaves the
        event in the state the other one needs, so they do not trigger each other
        again.
        """
        res = super().write(vals)
        if vals.get("website_published"):
            self._move_to_published_stage()
        elif "stage_id" in vals:
            self._publish_in_published_stage()
        return res

    def action_publish_event(self):
        self.website_published = True

    def _move_to_published_stage(self):
        """Move the events that are not in a published stage to the first one."""
        stage = self.env["event.stage"].search(
            [("pipe_publish", "=", True)], order="sequence", limit=1
        )
        events = self.filtered(lambda event: not event.stage_id.pipe_publish)
        if stage and events:
            events.stage_id = stage

    def _publish_in_published_stage(self):
        """Publish the events that are in a published stage."""
        self.filtered(
            lambda event: event.stage_id.pipe_publish and not event.website_published
        ).action_publish_event()
