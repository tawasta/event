from odoo import fields, models


class EventMailScheduler(models.Model):
    # 1. Private attributes
    _inherit = "event.mail"

    def update_feedback_survey(self, mail):
        registrations = mail.mail_registration_ids.mapped("registration_id")
        if mail.template_id.is_feedback_email:
            if mail.feedback_survey_id:
                registrations.write({'feedback_survey_id': mail.feedback_survey_id.id})
            elif mail.event_id.feedback_survey_id and not mail.feedback_survey_id:
                registrations.write({'feedback_survey_id': mail.event_id.feedback_survey_id.id})


    def process_registrations_based_on_interval(self, mail):
        # Apufunktio, joka käsittelee rekisteröintirivit interval_type perusteella
        lines = []
        is_mail_valid = False

        # Suodatetaan rekisteröinnit mail.interval_type perusteella
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
        # Tarkista, voidaanko sähköposti lähettää
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
        for mail in self:

            # Hae aktiivisen sivuston rajoitetut sähköpostipohjat
            Website = self.env["website"].sudo()
            current_website = Website.get_current_website()
            restricted_templates = current_website.restricted_mail_template_ids.ids
            is_restricted_template = mail.template_id.id in restricted_templates

            if mail.event_id.date_end < now:
                if not is_restricted_template:

                    # Kutsutaan apufunktiota ja saadaan sekä käsitellyt rivit että mailin tila
                    lines, is_mail_valid = self.process_registrations_based_on_interval(
                        mail
                    )
                    # Jos mail on validi ja on käsiteltyjä rivejä, päivitä mail_registration_ids
                    if is_mail_valid:
                        mail.write({"mail_registration_ids": lines})
                        self.update_feedback_survey(mail)
                        mail.mail_registration_ids.execute()
                    else:
                        mail_was_sent = self.check_and_send_mail(mail)
                        if mail_was_sent:

                            if mail.template_id.is_feedback_email:
                                registrations = mail.event_id.registration_ids.filtered(lambda r: r.state != 'cancel')
                                if mail.feedback_survey_id:
                                    registrations.write({'feedback_survey_id': mail.feedback_survey_id.id})
                                elif mail.event_id.feedback_survey_id and not mail.feedback_survey_id:
                                    registrations.write({'feedback_survey_id': mail.event_id.feedback_survey_id.id})

                            mail.event_id.mail_attendees(mail.template_id.id)
                            mail.write({"mail_sent": True})

            else:

                # Kutsutaan apufunktiota ja saadaan sekä käsitellyt rivit että mailin tila
                lines, is_mail_valid = self.process_registrations_based_on_interval(
                    mail
                )
                # Jos mail on validi ja on käsiteltyjä rivejä, päivitä mail_registration_ids
                if is_mail_valid:
                    mail.write({"mail_registration_ids": lines})
                    self.update_feedback_survey(mail)
                    mail.mail_registration_ids.execute()
                else:
                    mail_was_sent = self.check_and_send_mail(mail)
                    if mail_was_sent:

                        if mail.template_id.is_feedback_email:
                            registrations = mail.event_id.registration_ids.filtered(lambda r: r.state != 'cancel')
                            if mail.feedback_survey_id:
                                registrations.write({'feedback_survey_id': mail.feedback_survey_id.id})
                            elif mail.event_id.feedback_survey_id and not mail.feedback_survey_id:
                                registrations.write({'feedback_survey_id': mail.event_id.feedback_survey_id.id})

                        mail.event_id.mail_attendees(mail.template_id.id)
                        mail.write({"mail_sent": True})
        return True
