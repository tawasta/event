import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)

_INTERVALS = {
    "hours": lambda interval: relativedelta(hours=interval),
    "days": lambda interval: relativedelta(days=interval),
    "weeks": lambda interval: relativedelta(days=7 * interval),
    "months": lambda interval: relativedelta(months=interval),
    "now": lambda interval: relativedelta(hours=0),
}


class EventMailScheduler(models.Model):
    """Event automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on events since Odoo 9. A cron exists
    that periodically checks for mailing to run."""

    # 1. Private attributes
    _inherit = "event.mail"

    # 2. Fields declaration
    interval_type = fields.Selection(
        selection_add=[
            ("after_wait", "After registering to waiting list"),
            (
                "after_seats_available",
                "After more seats are available send to waiting list registrations",
            ),
        ],
        ondelete={"after_wait": "cascade", "after_seats_available": "cascade"},
    )

    def process_registrations_based_on_interval(self, scheduler, now):
        new_registrations, is_mail_valid = super(
            EventMailScheduler, self
        ).process_registrations_based_on_interval(scheduler, now)

        if scheduler.interval_type == "after_wait":
            new_registrations = (
                scheduler.event_id.registration_ids.filtered_domain(
                    [("state", "=", "wait")]
                )
                - scheduler.mail_registration_ids.registration_id
            )
            is_mail_valid = True

        if scheduler.interval_type == "after_seats_available":
            new_registrations = (
                scheduler.event_id.registration_ids.filtered_domain(
                    [("state", "=", "wait"), ("waiting_list_to_confirm", "=", True)]
                )
                - scheduler.mail_registration_ids.registration_id
            )
            is_mail_valid = True

        return new_registrations, is_mail_valid

    def check_and_send_mail(self, scheduler, now):
        if (
            scheduler.interval_type in ["after_wait", "after_seats_available"]
            and not scheduler.event_id.stage_id.cancel
        ):
            return True
        return super(EventMailScheduler, self).check_and_send_mail(scheduler, now)


class EventMailRegistration(models.Model):
    _inherit = "event.mail.registration"

    def execute(self):
        super(EventMailRegistration, self).execute()  # Call the original method
        now = fields.Datetime.now()
        todo = self.filtered(
            lambda reg_mail: reg_mail.scheduler_id.interval_type
            in ["after_wait", "after_seats_available"]
        )
        for reg_mail in todo:
            if (
                not reg_mail.mail_sent
                and reg_mail.registration_id.state == "wait"
                and (reg_mail.scheduled_date and reg_mail.scheduled_date <= now)
                and reg_mail.scheduler_id.notification_type == "mail"
            ):
                organizer = reg_mail.scheduler_id.event_id.organizer_id
                company = self.env.company
                author = self.env.ref("base.user_root")
                if organizer.email:
                    author = organizer
                elif company.email:
                    author = company.partner_id
                elif self.env.user.email:
                    author = self.env.user

                email_values = {
                    "author_id": author.id,
                }
                template = None
                try:
                    template = reg_mail.scheduler_id.template_ref.exists()
                except MissingError:
                    pass

                if not template:
                    _logger.warning(
                        "Cannot process ticket %s, because Mail Scheduler %s has reference to non-existent template",
                        reg_mail.registration_id,
                        reg_mail.scheduler_id,
                    )
                    continue

                if not template.email_from:
                    email_values["email_from"] = author.email_formatted
                template.send_mail(
                    reg_mail.registration_id.id, email_values=email_values
                )
                reg_mail.mail_sent = True

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    # @api.depends(
    #     "event_id.date_begin", "interval_type", "interval_unit", "interval_nbr"
    # )
    # def _compute_scheduled_date(self):
    #     for mail in self:
    #         if mail.interval_type in [
    #             "after_sub",
    #             "after_wait",
    #             "after_seats_available",
    #         ]:
    #             date, sign = mail.event_id.create_date, 1
    #         elif mail.interval_type == "before_event":
    #             date, sign = mail.event_id.date_begin, -1
    #         else:
    #             date, sign = mail.event_id.date_end, 1

    #         mail.scheduled_date = (
    #             date + _INTERVALS[mail.interval_unit](sign * mail.interval_nbr)
    #             if date
    #             else False
    #         )

    # @api.depends(
    #     "mail_sent",
    #     "interval_type",
    #     "event_id.registration_ids",
    #     "mail_registration_ids",
    #     "mail_registration_ids.mail_sent",
    # )
    # def _compute_done(self):
    #     for mail in self:
    #         if mail.interval_type in ["before_event", "after_event"]:
    #             mail.done = mail.mail_sent
    #         elif len(mail.mail_registration_ids) > 0:
    #             mail.done = all(mail.mail_sent for mail in mail.mail_registration_ids)

    # # 5. Constraints and onchanges

    # # 6. CRUD methods

    # # 7. Action methods
    # def process_registrations_based_on_interval(self, mail):
    #     lines, is_mail_valid = super(
    #         EventMailScheduler, self
    #     ).process_registrations_based_on_interval(mail)
    #     lines = []
    #     is_mail_valid = False

    #     if mail.interval_type in [
    #         "after_sub",
    #         "after_wait",
    #         "after_seats_available",
    #     ]:
    #         # update registration lines
    #         lines = [
    #             (0, 0, {"registration_id": registration.id})
    #             for registration in (
    #                 mail.event_id.registration_ids
    #                 - mail.mapped("mail_registration_ids.registration_id")
    #             )
    #             if (mail.interval_type == "after_sub" and registration.state == "open")
    #             or (mail.interval_type == "after_wait" and registration.state == "wait")
    #             or (
    #                 mail.interval_type == "after_seats_available"
    #                 and registration.state == "wait"
    #                 and registration.waiting_list_to_confirm
    #             )
    #         ]

    #         is_mail_valid = True

    #     return lines, is_mail_valid

    # def check_and_send_mail(self, mail):
    #     now = fields.Datetime.now()
    #     can_send = super().check_and_send_mail(mail)
    #     can_send = False

    #     if (
    #         not mail.mail_sent
    #         and mail.scheduled_date <= now
    #         and mail.notification_type == "mail"
    #         and (mail.interval_type != "before_event" or mail.event_id.date_end > now)
    #         and not mail.event_id.stage_id.cancel
    #     ):
    #         can_send = True

    #     return can_send

    # 8. Business methods
