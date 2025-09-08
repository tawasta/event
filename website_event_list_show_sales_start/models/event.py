from odoo import fields, models


class Event(models.Model):

    _inherit = "event.event"

    event_ticket_earliest_start_sale = fields.Datetime(
        string="Earliest Ticket Start of Sale",
        compute="_compute_event_ticket_earliest_start_sale",
    )

    def _compute_event_ticket_earliest_start_sale(self):
        for event in self:
            event.event_ticket_earliest_start_sale = min(
                event.event_ticket_ids.filtered(
                    lambda ticket: ticket.start_sale_datetime
                ).mapped("start_sale_datetime"),
                default=False,
            )
