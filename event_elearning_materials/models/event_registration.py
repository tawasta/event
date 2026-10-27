import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    # Just to improve traceability of who gets enrolled
    attendee_partner_id = fields.Many2one(tracking=True)

    is_course_member = fields.Boolean(
        string="Enrolled in Course", compute="_compute_is_course_member", store=False
    )

    @api.depends("event_id.slide_channel_id", "attendee_partner_id")
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
        # Only confirmed registrations granted course access, so only their
        # cancellation removes it. Cancelling a draft registration or a later
        # write on a cancelled one must not remove access gained some other way.
        confirmed_registrations = self.filtered(
            lambda reg: reg.state in ("open", "done")
        )

        res = super().write(vals)

        for registration in self:
            event = registration.event_id
            course = event.slide_channel_id
            partner = registration.attendee_partner_id

            if not course or not partner:
                continue

            if registration.state == "open" and not registration.is_course_member:
                registration._enroll_attendees_in_course()

        confirmed_registrations.filtered(
            lambda reg: reg.state == "cancel"
        )._remove_attendee_from_course()

        return res

    def _remove_attendee_from_course(self):
        """
        Remove the attendees of cancelled registrations from the related course,
        unless another confirmed registration still gives them access
        """
        for registration in self:
            course = registration.event_id.slide_channel_id
            partner = registration.attendee_partner_id
            if not course or not partner:
                continue
            if registration._has_course_registration_from_other_event():
                continue

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
            if not channel_partner:
                continue

            channel_partner.unlink()
            registration._message_log(
                body=_(
                    "Attendee removed from the course %(course)s",
                    course=course.name,
                )
            )

    def _has_course_registration_from_other_event(self):
        """
        Whether the attendee has another confirmed registration on an event
        linked to the same course
        """
        self.ensure_one()
        other_registration_count = (
            self.env["event.registration"]
            .sudo()
            .search_count(
                [
                    ("id", "!=", self.id),
                    ("attendee_partner_id", "=", self.attendee_partner_id.id),
                    (
                        "event_id.slide_channel_id",
                        "=",
                        self.event_id.slide_channel_id.id,
                    ),
                    ("state", "in", ["open", "done"]),
                ],
                limit=1,
            )
        )
        return bool(other_registration_count)

    def _update_mail_schedulers(self):
        """
        Enroll confirmed attendees to the related course.

        Core calls this on every confirmation path: create, write to a
        confirmed state and sale order confirmation. The latter recomputes
        the state without calling write(), so write() alone would not be enough.
        """
        res = super()._update_mail_schedulers()
        self._enroll_attendees_in_course()
        return res

    def _enroll_attendees_in_course(self):
        confirmed_registrations = self.filtered(
            lambda reg: reg.state == "open"
            and reg.event_id.slide_channel_id
            and reg.attendee_partner_id
        )
        registrations_to_enroll = confirmed_registrations._filter_not_course_members()
        registrations_by_course = registrations_to_enroll.grouped(
            lambda reg: reg.event_id.slide_channel_id
        )
        for course, registrations in registrations_by_course.items():
            # A failing enrollment (e.g. the new user's email in
            # website_slides_core) must not roll back the sale order
            # confirmation or payment processing that confirmed the registration
            try:
                with self.env.cr.savepoint():
                    # sudo: the enrollment follows from a confirmed registration,
                    # and on-invitation courses would otherwise be skipped silently
                    # for users without eLearning rights (e.g. a salesperson)
                    course.sudo()._action_add_members(registrations.attendee_partner_id)
            except Exception as error:
                _logger.exception(
                    "Could not enroll registrations %s to course %s",
                    registrations.ids,
                    course.id,
                )
                body = _(
                    "Could not enroll the attendee to the course %(course)s: %(error)s",
                    course=course.name,
                    error=error,
                )
                for registration in registrations:
                    registration._message_log(body=body)
                continue
            body = _("Attendee enrolled to the course %(course)s", course=course.name)
            for registration in registrations:
                registration._message_log(body=body)

    def _filter_not_course_members(self):
        """
        Return the registrations whose attendee has not joined the course yet,
        so that repeated confirmation calls do not log duplicate notes. Invited
        attendees are kept: enrolling upgrades them to joined.
        """
        memberships = (
            self.env["slide.channel.partner"]
            .sudo()
            .search(
                [
                    ("channel_id", "in", self.event_id.slide_channel_id.ids),
                    ("partner_id", "in", self.attendee_partner_id.ids),
                    ("member_status", "!=", "invited"),
                ]
            )
        )
        enrolled = {(m.channel_id.id, m.partner_id.id) for m in memberships}
        return self.filtered(
            lambda reg: (reg.event_id.slide_channel_id.id, reg.attendee_partner_id.id)
            not in enrolled
        )
