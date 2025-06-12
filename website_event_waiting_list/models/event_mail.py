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
        (
            new_registrations,
            is_mail_valid,
        ) = super().process_registrations_based_on_interval(scheduler, now)

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
        return super().check_and_send_mail(scheduler, now)


class EventMailRegistration(models.Model):
    _inherit = "event.mail.registration"

    def execute(self):
        super().execute()  # Call the original method
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
                        "Cannot process ticket %s, because Mail Scheduler %s "
                        "has reference to non-existent template",
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

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
