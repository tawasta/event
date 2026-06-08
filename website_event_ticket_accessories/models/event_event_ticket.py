from odoo import fields, models


class EventEventTicket(models.Model):
    _inherit = "event.event.ticket"

    accessory_product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="event_event_ticket_accessory_product_rel",
        column1="event_ticket_id",
        column2="product_id",
        string="Lisätuotteet",
        domain=[("sale_ok", "=", True)],
        help="Products suggested in the cart when this event ticket is selected.",
    )