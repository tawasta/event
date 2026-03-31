import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    notification_sent = fields.Boolean(default=False, copy=False)

    ticket_sale_notification_sent = fields.Boolean(default=False, copy=False)

    @api.model
    def create(self, vals):
        _logger.info("event_active_notify: create called with vals=%s", vals)
        event = super().create(vals)

        if vals.get("is_published") and not event.notification_sent:
            event._notify_group_users()
        return event

    def write(self, vals):
        res = super().write(vals)
        if vals.get("is_published"):
            for event in self:
                if not event.notification_sent:
                    event._notify_group_users()
        return res

    def _notify_group_users(self):
        group = self.env.ref(
            "event_active_notify.group_event_notifications",
            raise_if_not_found=False,  # noqa: E501
        )
        template = self.env.ref(
            "event_active_notify.event_activation_internal_group_mail",
            raise_if_not_found=False,
        )
        _logger.info(
            "event_active_notify: group found=%s template found=%s",
            bool(group),
            bool(template),
        )
        if group and template:
            recipients = group.users
            _logger.info(
                "event_active_notify: recipients user_ids=%s",
                recipients.ids,
            )
            for event in self:
                for recipient in recipients:
                    template.with_context(
                        lang=recipient.lang or self.env.user.lang,
                    ).send_mail(
                        event.id,
                        force_send=True,
                        email_values={"email_to": recipient.partner_id.email},
                    )
                event.notification_sent = True
                _logger.info(
                    "event_active_notify: marked notification_sent=True for event id=%s",
                    event.id,
                )

    @api.model
    def _cron_notify_ticket_sales_start(self):
        _logger.info("event_active_notify: _cron_notify_ticket_sales_start started")
        today = fields.Date.today()
        start_of_day = fields.Datetime.to_datetime(f"{today} 00:00:00")
        end_of_day = fields.Datetime.to_datetime(f"{today} 23:59:59")

        _logger.info(
            "event_active_notify: cron checking tickets between %s and %s",
            start_of_day,
            end_of_day,
        )

        tickets = self.env["event.event.ticket"].search(
            [
                ("start_sale_datetime", ">=", start_of_day),
                ("start_sale_datetime", "<=", end_of_day),
                ("event_id.ticket_sale_notification_sent", "=", False),
                ("event_id.active", "=", True),
            ]
        )

        _logger.info(
            "event_active_notify: cron found ticket ids=%s",
            tickets.ids,
        )

        # Poimi niihin liittyvät tapahtumat
        events = tickets.mapped("event_id")

        _logger.info(
            "event_active_notify: cron mapped event ids=%s",
            events.ids,
        )

        group = self.env.ref(
            "event_active_notify.group_event_notifications",
            raise_if_not_found=False,  # noqa: E501
        )
        template = self.env.ref(
            "event_active_notify.event_ticket_sale_start_mail",
            raise_if_not_found=False,
        )

        _logger.info(
            "event_active_notify: cron group found=%s template found=%s",
            bool(group),
            bool(template),
        )

        if not group or not template:
            _logger.warning(
                "event_active_notify: cron exiting because group or template is missing"
            )
            return

        recipients = group.users

        _logger.info(
            "event_active_notify: cron recipients user_ids=%s",
            recipients.ids,
        )

        for event in events:
            for recipient in recipients:
                template.with_context(
                    lang=recipient.lang or self.env.user.lang,
                ).send_mail(
                    event.id,
                    force_send=True,
                    email_values={"email_to": recipient.partner_id.email},
                )
            event.ticket_sale_notification_sent = True
