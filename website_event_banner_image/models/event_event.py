import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventType(models.Model):
    _inherit = "event.type"

    banner_image = fields.Image(
        readonly=False,
        store=True,
        max_width=1920,
        max_height=1080,
        verify_resolution=True,
    )


class EventEvent(models.Model):
    _inherit = "event.event"

    banner_image = fields.Image(
        readonly=False,
        store=True,
        max_width=1920,
        max_height=1080,
        verify_resolution=True,
        compute="_compute_banner_image",
    )

    @api.depends("event_type_id")
    def _compute_banner_image(self):
        """Set banner image from event type."""
        for event in self:
            if not event.event_type_id:
                event.banner_image = event.banner_image or None
            else:
                event.banner_image = event.event_type_id.banner_image or None
