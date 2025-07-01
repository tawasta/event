import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    event_ticket_qty_discount_ids = fields.One2many(
        "event.ticket.qty.discount",
        "product_template_id",
        string="Ticket Quantity Discounts",
    )

    def copy(self, default=None):
        # Duplicate also the discount rules when duplicating a product
        default = dict(default or {})

        res = super().copy(default)

        qty_discount_obj = self.env["event.ticket.qty.discount"]

        for event_ticket_qty_discount_id in self.event_ticket_qty_discount_ids:
            qty_discount_obj.create(
                {
                    "ticket_number": event_ticket_qty_discount_id.ticket_number,
                    "discount": event_ticket_qty_discount_id.discount,
                    "product_template_id": res.id,
                }
            )

        return res

    @api.constrains("event_ticket_qty_discount_ids")
    def _check_ticket_qty_discount_sequence(self):
        # Check that running numbers are used
        for product_template in self:
            expected = 1
            for discount in product_template.event_ticket_qty_discount_ids:
                if discount.ticket_number != expected:
                    raise ValidationError(
                        _("Ticket number sequence should be ascending with no gaps.")
                    )
                expected += 1
