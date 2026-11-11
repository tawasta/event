import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    notification_sent = fields.Boolean(default=False, copy=False)
    ticket_sale_notification_sent = fields.Boolean(default=False, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        published = events.browse(
            [
                event.id
                for event, vals in zip(events, vals_list, strict=True)
                if vals.get("is_published")
            ]
        )
        published._notify_group_users()
        return events

    def write(self, vals):
        res = super().write(vals)
        if vals.get("is_published"):
            self._notify_group_users()
        return res

    def _notify_group_users(self):
        """Tell the notification group about events that were just published."""
        events = self.filtered(lambda event: not event.notification_sent)
        if events and events._send_to_notification_group(
            "event_active_notify.event_activation_internal_group_mail"
        ):
            events.notification_sent = True

    @api.model
    def _cron_notify_ticket_sales_start(self):
        """Tell the notification group about events whose ticket sale starts today."""
        today_start = fields.Datetime.today()
        events = self.search(
            [
                ("ticket_sale_notification_sent", "=", False),
                (
                    "event_ticket_ids",
                    "any",
                    [
                        ("start_sale_datetime", ">=", today_start),
                        ("start_sale_datetime", "<", today_start + timedelta(days=1)),
                    ],
                ),
            ]
        )
        if events and events._send_to_notification_group(
            "event_active_notify.event_ticket_sale_start_mail"
        ):
            events.ticket_sale_notification_sent = True

    def _send_to_notification_group(self, template_xmlid):
        """Send the template of every event to each user of the notification group.

        :return: False when the group or the template is missing and nothing was sent
        """
        group = self.env.ref(
            "event_active_notify.group_event_notifications",
            raise_if_not_found=False,
        )
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not group or not template:
            _logger.warning(
                "Event notification skipped: group or template %s is missing",
                template_xmlid,
            )
            return False
        # The mails are queued, not sent at once: the queue is committed together
        # with the "notification sent" flag, so a failure never causes duplicates.
        for recipient in group.user_ids.filtered("partner_id.email"):
            template.with_context(
                lang=recipient.lang or self.env.user.lang
            ).send_mail_batch(
                self.ids,
                email_values={"email_to": recipient.partner_id.email},
            )
        return True
