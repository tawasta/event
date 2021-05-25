##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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

# 1. Standard library imports:
from dateutil.relativedelta import relativedelta

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models, api, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_INTERVALS = {
    "hours": lambda interval: relativedelta(hours=interval),
    "days": lambda interval: relativedelta(days=interval),
    "weeks": lambda interval: relativedelta(days=7 * interval),
    "months": lambda interval: relativedelta(months=interval),
    "now": lambda interval: relativedelta(hours=0),
}


class EventTypeMail(models.Model):
    """ Template of event.mail to attach to event.type. Those will be copied
    upon all events created in that type to ease event creation. """

    # 1. Private attributes
    _inherit = "event.type.mail"

    # 2. Fields declaration
    interval_type = fields.Selection(
        [
            ("after_sub", "After each registration"),
            ("after_wait", "After registering to waiting list"),
            (
                "after_seats_available",
                "After more seats are available send to waiting list registrations",
            ),
            ("before_event", "Before the event"),
            ("after_event", "After the event"),
        ],
        string="Trigger",
        default="before_event",
        required=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class EventMailScheduler(models.Model):
    """ Event automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on events since Odoo 9. A cron exists
    that periodically checks for mailing to run. """

    # 1. Private attributes
    _inherit = "event.mail"

    # 2. Fields declaration
    interval_type = fields.Selection(
        [
            ("after_sub", "After each registration"),
            ("after_wait", "After registering to waiting list"),
            (
                "after_seats_available",
                "After more seats are available send to waiting list registrations",
            ),
            ("before_event", "Before the event"),
            ("after_event", "After the event"),
        ],
        string="Trigger",
        default="before_event",
        required=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends(
        "event_id.date_begin", "interval_type", "interval_unit", "interval_nbr"
    )
    def _compute_scheduled_date(self):
        for mail in self:
            if mail.interval_type in [
                "after_sub",
                "after_wait",
                "after_seats_available",
            ]:
                date, sign = mail.event_id.create_date, 1
            elif mail.interval_type == "before_event":
                date, sign = mail.event_id.date_begin, -1
            else:
                date, sign = mail.event_id.date_end, 1

            mail.scheduled_date = (
                date + _INTERVALS[mail.interval_unit](sign * mail.interval_nbr)
                if date
                else False
            )

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def execute(self):
        for mail in self:
            now = fields.Datetime.now()
            if mail.interval_type in [
                "after_sub",
                "after_wait",
                "after_seats_available",
            ]:
                lines = [
                    (0, 0, {"registration_id": registration.id})
                    for registration in (
                        mail.event_id.registration_ids
                        - mail.mapped("mail_registration_ids.registration_id")
                    )
                    if (
                        mail.interval_type == "after_sub"
                        and registration.state == "open"
                    )
                    or (
                        mail.interval_type == "after_wait"
                        and registration.state == "wait"
                    )
                    or (
                        mail.interval_type == "after_seats_available"
                        and registration.waiting_list_to_confirm
                    )
                ]
                if lines:
                    mail.write({"mail_registration_ids": lines})
                # execute scheduler on open registrations
                mail.mail_registration_ids.execute()

            else:
                # Do not send emails if the mailing was scheduled
                # before the event but the event is over
                if (
                    not mail.mail_sent
                    and mail.scheduled_date <= now
                    and mail.notification_type == "mail"
                    and (
                        mail.interval_type != "before_event"
                        or mail.event_id.date_end > now
                    )
                ):
                    mail.event_id.mail_attendees(mail.template_id.id)
                    mail.write({"mail_sent": True})
        return True

    # 8. Business methods


class EventMailRegistration(models.Model):

    # 1. Private attributes
    _inherit = "event.mail.registration"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def execute(self):
        now = fields.Datetime.now()
        todo = self.filtered(
            lambda reg_mail: (
                not reg_mail.mail_sent
                and reg_mail.registration_id.state in ["open", "done", "wait"]
                and (reg_mail.scheduled_date and reg_mail.scheduled_date <= now)
                and reg_mail.scheduler_id.notification_type == "mail"
                and reg_mail.scheduler_id.interval_type != "after_seats_available"
            )
            or (
                reg_mail.scheduler_id.interval_type == "after_seats_available"
                and reg_mail.registration_id.waiting_list_to_confirm
                and not reg_mail.mail_sent
                and (reg_mail.scheduled_date and reg_mail.scheduled_date <= now)
                and reg_mail.scheduler_id.notification_type == "mail"
            )
        )
        for reg_mail in todo:
            reg_mail.scheduler_id.template_id.send_mail(reg_mail.registration_id.id)
        todo.write({"mail_sent": True})

    # 8. Business methods
