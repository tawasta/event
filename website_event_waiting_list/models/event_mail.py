import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

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
