import logging

from odoo import models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    def write(self, vals):
        res = super().write(vals)
        self.action_set_stage_published(vals.get("stage_id"))
        return res

    def action_publish_event(self):
        self.website_published = True

    def action_set_stage_published(self, stage_id):
        if (
            stage_id
            and len(
                self.env["event.stage"].search(
                    [("id", "=", stage_id), ("pipe_publish", "=", True)]
                )
            )
            > 0
        ):
            self.action_publish_event()
