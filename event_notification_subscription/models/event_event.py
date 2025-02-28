from odoo import models, fields, api

class Event(models.Model):
    _inherit = "event.event"

    announcement_sent = fields.Boolean(
        string="Announcement Sent",
        default=False,
        help="Indicates if an announcement email has already been sent for this event."
    )

    @api.model
    def send_event_notifications(self):
        """Lähettää sähköpostit kontakteille, jotka ovat kiinnostuneet tapahtuman tageista."""
        events = self.search([("is_published", "=", True), ("announcement_sent", "=", False)])

        for event in events:
            interested_partners = self.env["res.partner"].search([
                ("event_interest_tags", "in", event.tag_ids.ids)
            ])
            
            if interested_partners:
                # TODO Lahetetaan sposti
                # Minkalainen viesti lahetetaan

                event.announcement_sent = True  # Merkitään, että tiedote on lähetetty
