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
