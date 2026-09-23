from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    cart_suggested_event_ids = fields.Many2many(
        comodel_name="event.event",
        relation="event_event_cart_suggested_event_rel",
        column1="event_id",
        column2="suggested_event_id",
        string="Suggested Events in Cart",
        help=(
            "Events suggested in the webshop cart when this event has been "
            "selected. Suggested events are not added to the cart automatically."
        ),
    )
