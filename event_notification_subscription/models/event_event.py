from odoo import Command, api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    announcement_sent = fields.Boolean(
        string="Announcement to Interested Contacts Sent",
        default=False,
        copy=False,
        help="Indicates if an announcement email has already been sent for this "
        "event to contacts who are interested in this event's tags.",
    )

    @api.model
    def _send_event_notifications(self):
        """Announce new events to the contacts interested in the tags of the event."""
        # Past and finished events are excluded, so that they are not announced
        events = self.search(
            [
                ("is_published", "=", True),
                ("date_begin", ">=", fields.Datetime.now()),
                ("stage_id.pipe_end", "=", False),
                ("announcement_sent", "=", False),
            ]
        )
        if not events:
            return
        template = self.env.ref(
            "event_notification_subscription.tag_based_notification_mail"
        )
        interested_partners = self.env["res.partner"].search(
            [
                ("event_interest_tags", "in", events.tag_ids.ids),
                ("email", "!=", False),
            ]
        )
        for event in events:
            recipients = interested_partners.filtered(
                lambda partner, event=event: partner.event_interest_tags
                & event.tag_ids
            )
            if recipients:
                template.send_mail(
                    event.id,
                    email_values={
                        "auto_delete": True,
                        "recipient_ids": [Command.set(recipients.ids)],
                        "partner_ids": [],
                    },
                )
        events.announcement_sent = True
