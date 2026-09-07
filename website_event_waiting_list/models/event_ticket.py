from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventTicket(models.Model):
    # 1. Private attributes
    _inherit = "event.event.ticket"

    # 2. Fields declaration

    # TODO: Seems like seats_waiting is not used anywhere? / JK
    seats_waiting = fields.Integer(
        string="Waiting Seats",
        # The compute is removed because it's broken.
        # It doesn't assign any values for field and leads to an error
        # compute="_compute_seats",
    )

    waiting_list = fields.Boolean(
        related="event_id.waiting_list",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("seats_max", "event_id.waiting_list", "event_id.seats_limited")
    def _compute_seats_limited(self):
        """A ticket with no limit of its own is still bound by its event's
        overall limit, if the event has one. Without this, every check that
        relies on seats_limited/seats_available (cart quantity, sold-out
        badges, registration_open) only ever look at the ticket's own,
        non-existent limit and let the event's capacity be bypassed."""
        res = super()._compute_seats_limited()
        for ticket in self:
            if (
                not ticket.seats_limited
                and ticket.event_id.waiting_list
                and ticket.event_id.seats_limited
            ):
                ticket.seats_limited = True
        return res

    @api.depends(
        "seats_max",
        "registration_ids.state",
        "registration_ids.active",
        "event_id.seats_available",
        "event_id.waiting_list",
        "event_id.seats_limited",
    )
    def _compute_seats(self):
        """A ticket's own limit and its event's overall limit are independent
        - whichever is tighter is the one that should actually apply, not
        just whichever the ticket happens to have configured."""
        res = super()._compute_seats()
        for ticket in self:
            if not (ticket.event_id.waiting_list and ticket.event_id.seats_limited):
                continue
            if not ticket.seats_max:
                ticket.seats_available = ticket.event_id.seats_available
            else:
                ticket.seats_available = min(
                    ticket.seats_available, ticket.event_id.seats_available
                )
        return res

    @api.depends(
        "seats_limited", "seats_available", "event_id.event_registrations_sold_out"
    )
    def _compute_is_sold_out(self):
        """Extend the original method: a negative seats_available (ticket or
        inherited event limit oversold) is truthy in Python, so core's
        `not ticket.seats_available` check wrongly leaves it not sold out."""
        res = super()._compute_is_sold_out()
        for ticket in self:
            if ticket.seats_limited and ticket.seats_available < 0:
                ticket.is_sold_out = True
        return res

    @api.constrains("registration_ids", "seats_max")
    def _check_seats_availability(self, minimal_availability=0):
        sold_out_tickets = []
        for ticket in self:
            if (
                ticket.seats_max
                and ticket.seats_available < minimal_availability
                and not ticket.event_id.waiting_list
            ):
                sold_out_tickets.append(
                    _(
                        '- the ticket "%(ticket_name)s" (%(event_name)s): '
                        "Missing %(nb_too_many)i seats.",
                        ticket_name=ticket.name,
                        event_name=ticket.event_id.name,
                        nb_too_many=-ticket.seats_available,
                    )
                )
        if sold_out_tickets:
            raise ValidationError(
                _("There are not enough seats available for:")
                + "\n%s\n" % "\n".join(sold_out_tickets)
            )

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
