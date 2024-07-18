from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventTicket(models.Model):

    # 1. Private attributes
    _inherit = "event.event.ticket"

    # 2. Fields declaration
    seats_waiting = fields.Integer(
        string="Waiting Seats", compute="_compute_seats", store=True
    )

    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        compute="_compute_waiting_list",
        help="Enable waiting list when attendee limit is reached.",
        readonly=False,
        store=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_id", "waiting_list")
    def _compute_waiting_list(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for ticket in self:
            ticket.waiting_list = ticket.event_id.waiting_list

    # @api.depends("seats_max", "registration_ids")
    # def _compute_seats(self):
    #     """
    #     Determine reserved, available, reserved but unconfirmed,
    #     used and waiting seats.
    #     """
    #     # initialize fields to 0 + compute seats availability
    #     for ticket in self:
    #         ticket.seats_unconfirmed = (
    #             ticket.seats_reserved
    #         ) = ticket.seats_used = ticket.seats_available = ticket.seats_waiting = 0
    #     # aggregate registrations by ticket and by state
    #     if self.ids:
    #         state_field = {
    #             "draft": "seats_unconfirmed",
    #             "open": "seats_reserved",
    #             "done": "seats_used",
    #             "wait": "seats_waiting",
    #         }
    #         query = """ SELECT event_ticket_id, state, count(event_id)
    #                     FROM event_registration
    #                     WHERE event_ticket_id IN %s AND state IN
    #                     ('draft', 'open', 'done', 'wait')
    #                     GROUP BY event_ticket_id, state
    #                 """
    #         self.env["event.registration"].flush(
    #             ["event_id", "event_ticket_id", "state"]
    #         )
    #         self.env.cr.execute(query, (tuple(self.ids),))
    #         for event_ticket_id, state, num in self.env.cr.fetchall():
    #             ticket = self.browse(event_ticket_id)
    #             ticket[state_field[state]] += num
    #     # compute seats_available
    #     for ticket in self:
    #         if ticket.seats_max > 0:
    #             ticket.seats_available = ticket.seats_max - (
    #                 ticket.seats_reserved + ticket.seats_used
    #             )

    # 5. Constraints and onchanges
    # @api.constrains("seats_available", "seats_max")
    # def _constrains_seats_available(self):
    #     for ticket in self:
    #         if ticket.seats_max and ticket.seats_available < 0:
    #             raise ValidationError(_("No more available seats for this ticket."))

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
                        '- the ticket "%(ticket_name)s" (%(event_name)s): Missing %(nb_too_many)i seats.',
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
