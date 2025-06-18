from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    event_ticket_qty_discount_ids = fields.One2many(
        "event.ticket.qty.discount",
        "product_template_id",
        string="Ticket Quantity Discounts",
    )

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
