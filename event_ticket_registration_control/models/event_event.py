from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

# An event that starts further away than this opens its ticket sales a month before
# the event. A nearer event opens them when it is published.
EARLY_SALES_DAYS = 60
# A nearer event can be published only by the users with additional rights
PUBLISH_RESTRICTION_DAYS = 30


class EventEvent(models.Model):
    _inherit = "event.event"

    requires_additional_rights_to_publish = fields.Boolean(
        string="Requires Additional Rights to Publish",
        compute="_compute_requires_additional_rights_to_publish",
    )
    is_published_sudo_helper = fields.Boolean(
        string="Is published (read as sudo)",
        compute="_compute_is_published_sudo_helper",
        help="Technical helper field so that all users can read the Is Published field",
    )

    @api.depends("date_begin")
    def _compute_requires_additional_rights_to_publish(self):
        # Not stored, as the result changes with the current date
        for event in self:
            event.requires_additional_rights_to_publish = bool(
                event.date_begin
                and event._get_days_until_start() < PUBLISH_RESTRICTION_DAYS
            )

    def _compute_is_published_sudo_helper(self):
        # The form view hides is_published from the users without the publishing
        # group (pelastuskoiraliitto_event_backend_management), so the warning of
        # the view uses this field
        for event in self:
            event.is_published_sudo_helper = event.is_published

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        events._create_default_ticket()
        events._update_ticket_sales_start()
        events._check_publishing_access()
        events.filtered("is_published")._open_ticket_sales()
        return events

    def write(self, vals):
        newly_published = self.browse()
        if vals.get("is_published"):
            newly_published = self.filtered(lambda event: not event.is_published)
        res = super().write(vals)
        if "date_begin" in vals or "event_ticket_ids" in vals:
            self._update_ticket_sales_start()
        if "date_begin" in vals or "is_published" in vals:
            self._check_publishing_access()
        if newly_published:
            newly_published._check_has_tickets()
            newly_published._open_ticket_sales()
        return res

    def _get_days_until_start(self):
        self.ensure_one()
        return (self.date_begin - fields.Datetime.today()).days

    def _get_placeholder_sales_start(self):
        """Return the start of the registration, from the start of the event.

        The start of a near event is only a placeholder: _open_ticket_sales sets
        the real one when the event is published.
        """
        self.ensure_one()
        if self._get_days_until_start() > EARLY_SALES_DAYS:
            return self.date_begin - timedelta(days=30)
        return self.date_begin

    def _get_published_sales_start(self):
        """Return the registration start of a published event that is near."""
        self.ensure_one()
        start_sale_datetime = fields.Datetime.now()
        if self._get_days_until_start() >= PUBLISH_RESTRICTION_DAYS:
            start_sale_datetime += timedelta(days=14)
        return start_sale_datetime

    def _create_default_ticket(self):
        """Create a free ticket for the events that have no tickets."""
        self.env["event.event.ticket"].create(
            [
                {
                    "event_id": event.id,
                    "name": self.env._("Standard Ticket"),
                    "price": 0.0,
                }
                for event in self.filtered(lambda event: not event.event_ticket_ids)
            ]
        )

    def _write_ticket_sales_start(self, tickets, start_sale_datetime):
        """Set the registration start of the tickets, and return the changed tickets.

        A ticket whose registration ends before the new start is left as it is.
        """
        tickets = tickets.filtered(
            lambda ticket: not ticket.end_sale_datetime
            or ticket.end_sale_datetime >= start_sale_datetime
        )
        # sudo: the tickets are controlled by the event, whatever the access rights
        # of the user to the tickets are
        tickets.sudo().write({"start_sale_datetime": start_sale_datetime})
        return tickets

    def _update_ticket_sales_start(self):
        """Set the registration start of the tickets by the start of the event.

        The sales of a published event that is near have been opened at the
        publishing, so only the tickets without a start, or with a start that is
        later than the opening of the sales, are opened.
        """
        for event in self:
            tickets = event.event_ticket_ids
            if event.is_published and event._get_days_until_start() <= EARLY_SALES_DAYS:
                open_start = event._get_published_sales_start()
                event._write_ticket_sales_start(
                    tickets.filtered(
                        lambda ticket, start=open_start: not ticket.start_sale_datetime
                        or ticket.start_sale_datetime > start
                    ),
                    open_start,
                )
            else:
                event._write_ticket_sales_start(
                    tickets, event._get_placeholder_sales_start()
                )

    def _check_has_tickets(self):
        """Force using tickets: the tickets must be saved before publishing."""
        if any(not event.event_ticket_ids for event in self):
            raise ValidationError(
                self.env._("Please add tickets to event before publishing.")
            )

    def _check_publishing_access(self):
        """Check that the user can publish the events.

        A user without the additional rights cannot
        * publish an event that starts in less than 30 days, or
        * move a published event so that it would start in less than 30 days.
        """
        if self.env.user.has_group(
            "event_ticket_registration_control.group_publish_event_in_near_future"
        ):
            return
        if any(
            event.is_published
            and event._get_days_until_start() < PUBLISH_RESTRICTION_DAYS
            for event in self
        ):
            raise ValidationError(
                self.env._(
                    "This event is set to start within 30 days. Publishing this "
                    "event requires additional access rights."
                )
            )

    def _open_ticket_sales(self):
        """Open the ticket sales of the published events that are near."""
        for event in self:
            if event._get_days_until_start() > EARLY_SALES_DAYS:
                continue
            opens_now = event._get_days_until_start() < PUBLISH_RESTRICTION_DAYS
            tickets = event._write_ticket_sales_start(
                event.event_ticket_ids, event._get_published_sales_start()
            )
            for ticket in tickets:
                event.message_post(
                    body=event._get_sales_opened_message(ticket, opens_now)
                )

    def _get_sales_opened_message(self, ticket, opens_now):
        self.ensure_one()
        if opens_now:
            return self.env._(
                "Event is less than 30 days away. Updated the sales of the ticket "
                "%(ticket)s to open now.",
                ticket=ticket.name,
            )
        return self.env._(
            "Event is 1-2 months away. Updated the sales of the ticket %(ticket)s to "
            "open two weeks from publishing.",
            ticket=ticket.name,
        )
