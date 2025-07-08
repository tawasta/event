from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    notification_sent = fields.Boolean(
        string="Notification Sent", default=False, copy=False
    )

    ticket_sale_notification_sent = fields.Boolean(
        string="Ticket Sale Notification Sent", default=False, copy=False
    )

    @api.model
    def create(self, vals):
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
            "event_active_notify.group_event_notifications", raise_if_not_found=False
        )
        template = self.env.ref(
            "event_active_notify.event_activation_internal_group_mail",
            raise_if_not_found=False,
        )
        if group and template:
            recipients = group.users
            for event in self:
                for recipient in recipients:
                    template.with_context(
                        lang=recipient.lang or self.env.user.lang,
                        email_to=recipient.partner_id.email,
                    ).send_mail(event.id, force_send=True)
                event.notification_sent = True

    @api.model
    def _cron_notify_ticket_sales_start(self):
        today = fields.Date.today()
        start_of_day = fields.Datetime.to_datetime(f"{today} 00:00:00")
        end_of_day = fields.Datetime.to_datetime(f"{today} 23:59:59")

        tickets = self.env['event.event.ticket'].search([
            ('start_sale_datetime', '>=', start_of_day),
            ('start_sale_datetime', '<=', end_of_day),
            ('event_id.ticket_sale_notification_sent', '=', False),
            ('event_id.active', '=', True),
        ])

        # Poimi niihin liittyvät tapahtumat
        events = tickets.mapped('event_id')

        group = self.env.ref(
            "event_active_notify.group_event_notifications", raise_if_not_found=False
        )
        template = self.env.ref(
            "event_active_notify.event_ticket_sale_start_mail",
            raise_if_not_found=False,
        )

        if not group or not template:
            return

        recipients = group.users

        for event in events:
            for recipient in recipients:
                template.with_context(
                    lang=recipient.lang or self.env.user.lang,
                    email_to=recipient.partner_id.email,
                ).send_mail(event.id, force_send=True)
            event.ticket_sale_notification_sent = True
