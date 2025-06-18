from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EventTicketQtyDiscount(models.Model):
    _name = "event.ticket.qty.discount"
    _description = "Event Ticket Quantity Discount"
    _order = "product_template_id asc, ticket_number asc"

    ticket_number = fields.Integer(string="Ticket #", required=True)
    discount = fields.Float(string="Discount %", required=True)
    product_template_id = fields.Many2one(
        "product.template", required=True, ondelete="cascade"
    )
