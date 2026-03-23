##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

import logging

from odoo import fields, models


class EventMailScheduler(models.Model):
    _inherit = "event.mail"

    def check_and_send_mail(self, mail):
        now = fields.Datetime.now()
        can_send = super().check_and_send_mail(mail)
        can_send = False
        if (
            not mail.mail_sent
            and mail.scheduled_date <= now
            and mail.notification_type == "mail"
            and (mail.interval_type != "before_event" or mail.event_id.date_end > now)
            and not mail.event_id.stage_id.cancel
        ):
            can_send = True

        return can_send


class EventMailRegistration(models.Model):
    _inherit = "event.mail.registration"

    def execute(self):
        now = fields.Datetime.now()
        todo = self.filtered(
            lambda reg_mail: not reg_mail.mail_sent
            and reg_mail.registration_id.state in ["open", "done"]
            and (reg_mail.scheduled_date and reg_mail.scheduled_date <= now)
            and reg_mail.scheduler_id.notification_type == "mail"
            and not reg_mail.registration_id.event_id.stage_id.cancel
        )
        for reg_mail in todo:
            logging.info("====CANCELLATION SEND EMAIL")
            logging.info(reg_mail)
            reg_mail.scheduler_id.template_id.send_mail(reg_mail.registration_id.id)
        todo.write({"mail_sent": True})
