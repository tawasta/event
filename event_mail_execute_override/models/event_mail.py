from odoo import fields, models, api, SUPERUSER_ID
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class EventMailScheduler(models.Model):
    _inherit = "event.mail"

    def update_feedback_survey(self, mail):
        registrations = mail.mail_registration_ids.mapped("registration_id")
        if mail.template_id.is_feedback_email:
            if mail.feedback_survey_id:
                registrations.write({"feedback_survey_id": mail.feedback_survey_id.id})
            elif mail.event_id.feedback_survey_id and not mail.feedback_survey_id:
                registrations.write(
                    {"feedback_survey_id": mail.event_id.feedback_survey_id.id}
                )

    def process_registrations_based_on_interval(self, mail):
        lines = []
        is_mail_valid = False

        if mail.interval_type == "after_sub":
            lines = [
                (0, 0, {"registration_id": registration.id})
                for registration in (
                    mail.event_id.registration_ids
                    - mail.mapped("mail_registration_ids.registration_id")
                )
            ]
            is_mail_valid = True

        return lines, is_mail_valid

    def check_and_send_mail(self, mail):
        now = fields.Datetime.now()
        if (
            not mail.mail_sent
            and mail.scheduled_date <= now
            and mail.notification_type == "mail"
            and (mail.interval_type != "before_event" or mail.event_id.date_end > now)
        ):
            return True
        return False

    def execute(self):
        now = fields.Datetime.now()
        delay_time = timedelta(minutes=1)
        start_time = datetime.now() + delay_time
        processed_mail_ids = set()  # Set to track processed mail IDs
        for mail in self:
            if mail.id in processed_mail_ids:
                _logger.info(f"Skipping already processed mail with ID {mail.id}")
                continue

            _logger.info(f"===EXECUTE ALOITUS mail_id: {mail.id}===")

            Website = self.env["website"].sudo()
            current_website = Website.get_current_website()
            restricted_templates = current_website.restricted_mail_template_ids.ids
            is_restricted_template = mail.template_id.id in restricted_templates

            if mail.event_id.date_end < now:
                if not is_restricted_template:
                    lines, is_mail_valid = self.process_registrations_based_on_interval(mail)
                    if is_mail_valid:
                        mail.write({"mail_registration_ids": lines})
                        self.update_feedback_survey(mail)
                        _logger.info(f"===LAHETETAAN EXECUTE 1 mail_id: {mail.id}===")
                        mail.mail_registration_ids.execute()
                    else:
                        mail_was_sent = self.check_and_send_mail(mail)
                        if mail_was_sent:
                            if mail.template_id.is_feedback_email:
                                registrations = mail.event_id.registration_ids.filtered(
                                    lambda r: r.state != "cancel"
                                )
                                if mail.feedback_survey_id:
                                    registrations.write({"feedback_survey_id": mail.feedback_survey_id.id})
                                elif (mail.event_id.feedback_survey_id and not mail.feedback_survey_id):
                                    registrations.write({"feedback_survey_id": mail.event_id.feedback_survey_id.id})
                            _logger.info(f"===LAHETETAAN MAIL ATTENDEES 1 mail_id: {mail.id}===")
                            mail.event_id.mail_attendees(mail.template_id.id)
                            mail.write({"mail_sent": True})
            else:
                lines, is_mail_valid = self.process_registrations_based_on_interval(mail)
                if is_mail_valid:
                    mail.write({"mail_registration_ids": lines})
                    self.update_feedback_survey(mail)
                    _logger.info(f"===LAHETETAAN EXECUTE 2 mail_id: {mail.id}===")
                    mail.mail_registration_ids.execute()
                else:
                    mail_was_sent = self.check_and_send_mail(mail)
                    if mail_was_sent:
                        if mail.template_id.is_feedback_email:
                            registrations = mail.event_id.registration_ids.filtered(lambda r: r.state != "cancel")
                            if mail.feedback_survey_id:
                                registrations.write({"feedback_survey_id": mail.feedback_survey_id.id})
                            elif (mail.event_id.feedback_survey_id and not mail.feedback_survey_id):
                                registrations.write({"feedback_survey_id": mail.event_id.feedback_survey_id.id})
                        _logger.info(f"===LAHETETAAN MAIL ATTENDEES 2 mail_id: {mail.id}===")
                        mail.event_id.mail_attendees(mail.template_id.id)
                        mail.write({"mail_sent": True})

            processed_mail_ids.add(mail.id)
            _logger.info(f"===EXECUTE LOPPUN mail_id: {mail.id}===")
        return True
