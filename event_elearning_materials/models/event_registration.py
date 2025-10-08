import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    is_course_member = fields.Boolean(
        string="Enrolled in Course", compute="_compute_is_course_member", store=False
    )

    @api.depends("event_id.slide_channel_id", "partner_id")
    def _compute_is_course_member(self):
        """
        Store if the event participant is enrolled on the event's related course
        """
        for reg in self:
            channel = reg.event_id.slide_channel_id
            partner = reg.attendee_partner_id
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
        """
        Check event registration state, and enroll/remove from the related course
        accordingly
        """

        res = super().write(vals)

        for registration in self:
            event = registration.event_id
            course = event.slide_channel_id
            partner = registration.attendee_partner_id

            if not course or not partner:
                continue

            if registration.state == "open" and not registration.is_course_member:
                course._action_add_members(partner)
            elif registration.state == "cancel" and registration.is_course_member:
                _logger.info("removing access")
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
        """
        Check event registration state, and enroll to the related course
        if registration confirmed
        """
        registrations = super().create(vals_list)
        for reg in registrations:
            if reg.state == "open" and reg.event_id.slide_channel_id:
                reg.event_id.slide_channel_id._action_add_members(reg.partner_id)
        return registrations
