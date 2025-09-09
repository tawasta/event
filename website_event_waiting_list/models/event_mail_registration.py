import logging

from odoo import fields, models
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)


class EventMailRegistration(models.Model):
    _inherit = "event.mail.registration"

    def execute(self):
        res = super().execute()  # Call the original method
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
                    _logger.warning("Template not found")
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
        return res
