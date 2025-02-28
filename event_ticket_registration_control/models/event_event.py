from odoo import models, fields, api
from datetime import timedelta
import logging


class Event(models.Model):
    _inherit = "event.event"

    @api.model
    def create(self, vals):
        """ Luo automaattisesti lipputuote ja asettaa sen ilmoittautumisen alkupäivämäärän """
        event = super(Event, self).create(vals)

        # Haetaan tapahtumaan liittyvät liput
        tickets = self.env["event.event.ticket"].search([("event_id", "=", event.id)])

        if not tickets:
            # Luodaan oletuslippu, jos tapahtumalle ei ole vielä lippuja
            ticket_vals = {
                "event_id": event.id,
                "name": "Standard Ticket",
                "price": 0.0,
                "start_sale_datetime": self._compute_registration_start(event.date_begin),
            }
            self.env["event.event.ticket"].create(ticket_vals)
        else:
            # Päivitetään kaikki olemassa olevat liput
            tickets.sudo().write({
                "start_sale_datetime": self._compute_registration_start(event.date_begin),
            })

        return event

    def write(self, vals):
        res = super(Event, self).write(vals)

        if "date_begin" or "event_ticket_ids" in vals:
            for event in self:
                tickets = self.env["event.event.ticket"].search([("event_id", "=", event.id)])
                for ticket in tickets:
                    ticket.sudo().write({
                        "start_sale_datetime": self._compute_registration_start(event.date_begin),
                    })

        return res

    def _compute_registration_start(self, event_start):
        """ Laskee rekisteröinnin aloituspäivämäärän tapahtuman päivämäärän perusteella """
        today = fields.Datetime.today()
        days_until_event = (event_start - today).days

        if days_until_event > 60:
            return event_start - timedelta(days=30)
        elif 30 <= days_until_event <= 60:
            return event_start - timedelta(days=14)
        else:
            return event_start - timedelta(days=3)
