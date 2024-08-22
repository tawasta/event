import logging

from odoo import fields, models


class EventMailScheduler(models.Model):
    # 1. Private attributes
    _inherit = "event.mail"

    def _custom_processing(self, scheduler, new_registrations):
        """Apufunktio, jota voidaan periä muissa moduuleissa"""

    def process_registrations_based_on_interval(self, scheduler, now):
        new_registrations = []
        is_mail_valid = False

        if scheduler.interval_type == "after_sub":
            new_registrations = (
                scheduler.event_id.registration_ids.filtered_domain(
                    [("state", "not in", ("cancel", "draft"))]
                )
                - scheduler.mail_registration_ids.registration_id
            )
            is_mail_valid = True

        return new_registrations, is_mail_valid

    def check_and_send_mail(self, scheduler, now):
        if scheduler.mail_done or scheduler.notification_type != "mail":
            return False
        if not scheduler.template_ref:
            return False
        if scheduler.scheduled_date <= now and (
            scheduler.interval_type != "before_event"
            or scheduler.event_id.date_end > now
        ):
            return True
        return False

    def execute(self):
        for scheduler in self:
            now = fields.Datetime.now()
            # delay_time = timedelta(minutes=1)
            # start_time = datetime.now() + delay_time
            Website = self.env["website"].sudo()
            current_website = Website.get_current_website()
            restricted_templates = current_website.restricted_mail_template_ids.ids
            is_restricted_template = scheduler.template_ref.id in restricted_templates

            (
                new_registrations,
                is_mail_valid,
            ) = self.process_registrations_based_on_interval(scheduler, now)
            if is_mail_valid:
                if is_restricted_template and scheduler.event_id.date_end <= now:
                    logging.info(
                        "Sähköpostipohja on rajoitettu eikä viestiä lähetetä, koska tapahtuma on päättynyt."  # noqa: B950
                    )
                    continue

                scheduler._create_missing_mail_registrations(new_registrations)
                # Kutsu apufunktiota
                self._custom_processing(scheduler, new_registrations)
                # execute scheduler on registrations
                logging.info("====EXECUTE=====");
                scheduler.mail_registration_ids.execute()
                total_sent = len(
                    scheduler.mail_registration_ids.filtered(lambda reg: reg.mail_sent)
                )
                scheduler.update(
                    {
                        "mail_done": total_sent
                        >= (
                            scheduler.event_id.seats_reserved
                            + scheduler.event_id.seats_used
                        ),
                        "mail_count_done": total_sent,
                    }
                )
            else:
                if is_restricted_template and scheduler.event_id.date_end <= now:
                    logging.info(
                        "Sähköpostipohja on rajoitettu eikä viestiä lähetetä, koska tapahtuma on päättynyt."  # noqa: B950
                    )
                    continue
                logging.info("=====SEN TMAIL=====");
                mail_was_sent = self.check_and_send_mail(scheduler, now)
                if mail_was_sent:
                    scheduler.event_id.mail_attendees(scheduler.template_ref.id)
                    scheduler.update(
                        {
                            "mail_done": True,
                            "mail_count_done": scheduler.event_id.seats_reserved
                            + scheduler.event_id.seats_used,
                        }
                    )
        return True
