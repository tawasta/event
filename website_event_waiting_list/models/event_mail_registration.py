from odoo import models


class EventMailRegistration(models.Model):

    # 1. Private attributes
    _inherit = "event.mail.registration"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    # def execute(self):
    #     now = fields.Datetime.now()
    #     todo = self.filtered(
    #         lambda reg_mail: (
    #             not reg_mail.mail_sent
    #             and reg_mail.registration_id.state in ["open", "done", "wait"]
    #             and (reg_mail.scheduled_date and reg_mail.scheduled_date <= now)
    #             and reg_mail.scheduler_id.notification_type == "mail"
    #             and (
    #                 (reg_mail.scheduler_id.interval_type != "after_seats_available")
    #                 or (
    #                     reg_mail.scheduler_id.interval_type == "after_seats_available"
    #                     and reg_mail.registration_id.state == "wait"
    #                     and reg_mail.registration_id.waiting_list_to_confirm
    #                 )
    #             )
    #             and not reg_mail.registration_id.event_id.stage_id.cancel
    #         )
    #     )
    #     delay_time = timedelta(minutes=1)
    #     start_time = datetime.now() + delay_time
    #     for reg_mail in todo:
    #         logging.info("===SEND EMAIL====")
    #         logging.info(reg_mail)
    #         reg_mail.scheduler_id.template_id.with_delay(eta=start_time).send_mail(
    #             reg_mail.registration_id.id, force_send=True
    #         )
    #     todo.write({"mail_sent": True})

    # 8. Business methods
