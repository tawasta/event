import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Event(models.Model):
    _inherit = "event.event"

    requires_additional_rights_to_publish = fields.Boolean(
        string="Requires Additional Rights to Publish",
        compute="_compute_requires_additional_rights_to_publish",
        store=True,
    )

    is_published_sudo_helper = fields.Boolean(
        string="Is published (read as sudo)",
        compute="_compute_is_published_sudo_helper",
        help="Technical helper field so that all users can read the Is Published field",
    )

    @api.model
    def create(self, vals):
        """Luo automaattisesti lipputuote ja asettaa sen
        ilmoittautumisen alkupäivämäärän"""
        event = super(Event, self).create(vals)

        ticket_obj = self.env["event.event.ticket"]

        # Haetaan tapahtumaan liittyvät liput
        tickets = ticket_obj.search([("event_id", "=", event.id)])

        if not tickets:
            # Luodaan oletuslippu, jos tapahtumalle ei ole vielä lippuja
            ticket_vals = {
                "event_id": event.id,
                "name": "Standard Ticket",
                "price": 0.0,
                "start_sale_datetime": self._compute_registration_start(
                    event.date_begin
                ),
            }
            ticket_obj.create(ticket_vals)
        else:
            # Päivitetään kaikki olemassa olevat liput
            tickets.sudo().write(
                {
                    "start_sale_datetime": self._compute_registration_start(
                        event.date_begin
                    ),
                }
            )

        # ensure the user was allowed to publish
        event._check_publishing_access()

        # If the event was created as published and it is <= 60 days away,
        # override placeholder ticket sale start based on publish timing
        if (
            event.is_published
            and (event.date_begin - fields.Datetime.today()).days <= 60
        ):
            event._open_ticket_sales()

        return event

    def write(self, vals):

        ticket_obj = self.env["event.event.ticket"]

        res = super(Event, self).write(vals)

        # Update the ticket sale start dates
        if "date_begin" in vals or "event_ticket_ids" in vals:
            for event in self:
                tickets = ticket_obj.search([("event_id", "=", event.id)])
                for ticket in tickets:
                    ticket.sudo().write(
                        {
                            "start_sale_datetime": self._compute_registration_start(
                                event.date_begin
                            ),
                        }
                    )

        # If start date or publishment got changed, run check
        # to ensure the user was allowed to publish
        if "date_begin" in vals or "is_published" in vals:
            for event in self:
                event._check_publishing_access()

        # If event gets published and it is <= 60 days away,
        # override placeholder ticket sale start based on publish timing
        if "is_published" in vals and vals["is_published"]:
            for event in self:
                if (event.date_begin - fields.Datetime.today()).days <= 60:
                    event._open_ticket_sales()

        return res

    def _compute_registration_start(self, event_start):
        """Laskee rekisteröinnin aloituspäivämäärän tapahtuman päivämäärän perusteella"""
        today = fields.Datetime.today()
        days_until_event = (event_start - today).days

        if days_until_event > 60:
            return event_start - timedelta(days=30)
        elif 30 <= days_until_event <= 60:
            # This is a placeholder start date - when the event that is 1-2 months away
            # gets published, the registration start will be set to two weeks from
            # publishing
            return event_start - timedelta(days=0)
        else:
            # This is a placeholder start date - when the event that is this close
            # gets published, the registration start will be set to the date of
            # publishing
            return event_start - timedelta(days=0)

    @api.depends("date_begin", "is_published")
    def _compute_requires_additional_rights_to_publish(self):
        # Check how many days until event, and set accordingly
        # if regular user is allowed to publish or not
        for event in self:

            today = fields.Datetime.today()
            days_until_event = (event.date_begin - today).days

            if days_until_event < 30:
                event.requires_additional_rights_to_publish = True
            else:
                event.requires_additional_rights_to_publish = False

    def _compute_is_published_sudo_helper(self):
        # Workaround to be able to use is_published in form view's field domain, as
        # sprintit_event_backend_management restricts read access to is_published

        for event in self.sudo():
            event.is_published_sudo_helper = event.is_published

    def _check_publishing_access(self):
        # Check if user without appropriate rights is trying to
        # * publish a new event that is < 30 days away, or
        # * trying to move an already published event so that it would be
        #   less than < 30 days away

        self.ensure_one()

        if (
            self.is_published
            and self.requires_additional_rights_to_publish
            and not self.env.user.has_group(
                "event_ticket_registration_control.group_publish_event_in_near_future"
            )
        ):
            raise ValidationError(
                _(
                    "This event is set to start within 30 days. Publishing this "
                    "event requires additional access rights."
                )
            )

    def _open_ticket_sales(self):
        self.ensure_one()

        ticket_obj = self.env["event.event.ticket"]
        tickets = ticket_obj.search([("event_id", "=", self.id)])

        today = fields.Datetime.today()
        days_until_event = (self.date_begin - today).days

        if days_until_event < 30:
            start_sale_datetime = fields.Datetime.now()
            message = _(
                "Event is less than 30 days away. Updated ticket '%s' sales to open now."
            )
        elif 30 <= days_until_event <= 60:
            start_sale_datetime = fields.Datetime.now() + timedelta(days=14)
            message = _(
                "Event is 1-2 months away. Updated ticket '%s' sales to "
                "open two weeks from publishing."
            )
        else:
            return

        for ticket in tickets:
            ticket.sudo().write({"start_sale_datetime": start_sale_datetime})

            self.message_post(body=message % ticket.name)
