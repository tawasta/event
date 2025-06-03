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

    @api.depends("slide_channel_id", "slide_channel_id.is_published")
    def _compute_slide_channel_url(self):
        # Get the URL so that it can be placed in the copy to clipboard widget

        for event in self:
            if event.slide_channel_id and event.slide_channel_id.is_published:
                event.slide_channel_url = event.slide_channel_id.website_url
            else:
                event.slide_channel_url = False

    def write(self, vals):
        res = super().write(vals)
        if "registration_ids" in vals or "slide_channel_id" in vals:
            for event in self:
                if event.slide_channel_id:
                    confirmed_registrations = event.registration_ids.filtered(
                        lambda r: r.state == "open"
                    )
                    partners = confirmed_registrations.mapped("partner_id")
                    event.slide_channel_id._action_add_members(partners)
        return res


class EventRegistration(models.Model):
    _inherit = "event.registration"

    is_course_member = fields.Boolean(
        string="Enrolled in Course", compute="_compute_is_course_member", store=False
    )

    @api.depends("event_id.slide_channel_id", "partner_id")
    def _compute_is_course_member(self):
        for reg in self:
            channel = reg.event_id.slide_channel_id
            partner = reg.partner_id
            if channel and partner:
                exists = (
                    self.env["slide.channel.partner"]
                    .sudo()
                    .search_count(
                        [
                            ("channel_id", "=", channel.id),
                            ("partner_id", "=", partner.id),
                        ]
                    )
                )
                reg.is_course_member = bool(exists)
            else:
                reg.is_course_member = False

    def write(self, vals):
        previous_states = dict((r.id, r.state) for r in self)
        res = super().write(vals)
        for registration in self:
            prev_state = previous_states.get(registration.id)
            new_state = registration.state
            event = registration.event_id
            course = event.slide_channel_id
            partner = registration.partner_id
            if not course or not partner:
                continue
            if prev_state != "open" and new_state == "open":
                course._action_add_members(partner)
            elif prev_state == "open" and new_state == "cancel":
                channel_partner = (
                    self.env["slide.channel.partner"]
                    .sudo()
                    .search(
                        [
                            ("channel_id", "=", course.id),
                            ("partner_id", "=", partner.id),
                        ],
                        limit=1,
                    )
                )
                if channel_partner:
                    channel_partner.unlink()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        registrations = super().create(vals_list)
        for reg in registrations:
            if reg.state == "open" and reg.event_id.slide_channel_id:
                reg.event_id.slide_channel_id._action_add_members(reg.partner_id)
        return registrations
