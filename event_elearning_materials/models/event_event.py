import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    slide_channel_id = fields.Many2one(
        "slide.channel",
        string="Related Course",
        help="Optional: When attendees are confirmed, "
        "they will be enrolled in this eLearning course automatically.",
    )

    slide_channel_url = fields.Char(
        string="Related Course URL",
        compute="_compute_slide_channel_url",
        store=True,
    )

    slide_channel_is_published = fields.Boolean(
        string="Related Course is Published", related="slide_channel_id.is_published"
    )

    @api.depends("slide_channel_id", "slide_channel_id.is_published")
    def _compute_slide_channel_url(self):
        """
        Get the URL so that it can be placed in the copy to clipboard widget
        """

        for event in self:
            if event.slide_channel_id and event.slide_channel_id.is_published:
                event.slide_channel_url = event.slide_channel_id.website_url
            else:
                event.slide_channel_url = False

    def write(self, vals):
        """
        Auto-enroll event attendees to the related course when the course is
        linked or changed. Access to a previously linked course is kept.
        """
        res = super().write(vals)
        if "registration_ids" in vals or "slide_channel_id" in vals:
            self.registration_ids._enroll_attendees_in_course()
        return res
