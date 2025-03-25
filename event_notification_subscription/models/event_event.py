import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Event(models.Model):
    _inherit = "event.event"

    announcement_sent = fields.Boolean(
        string="Announcement to Interested Contacts Sent",
        default=False,
        copy=False,
        help="""Indicates if an announcement email has already been sent for this event
          to contacts who are interested in this event's tags.""",
    )

    @api.model
    def _send_event_notifications(self):
        """Lähettää sähköpostit kontakteille, jotka ovat kiinnostuneet tapahtuman tageista."""

        now = fields.Datetime.now()

        # Exclude events that are in the past or have alredy been completed/cancelled
        events = self.search(
            [
                ("is_published", "=", True),
                ("date_begin", ">=", now),
                ("stage_id.pipe_end", "=", False),
                ("announcement_sent", "=", False),
            ]
        )

        for event in events:

            # Find contacts that have expressed interest in this event's tags
            interested_partners = self.env["res.partner"].search(
                [
                    ("event_interest_tags", "in", event.tag_ids.ids),
                    ("email", "!=", False),
                ]
            )

            recipient_partner_ids = [p.id for p in interested_partners]

            mail_template = self.env.ref(
                "event_notification_subscription.tag_based_notification_mail"
            )

            email_values = {
                "auto_delete": True,
                "message_type": "email",
                "recipient_ids": [(6, 0, recipient_partner_ids)],
                "partner_ids": [],
            }

            mail_template.send_mail(
                event.id, force_send=True, email_values=email_values
            )

            event.announcement_sent = True  # Merkitään, että tiedote on lähetetty
