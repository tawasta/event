from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductQuantityAutoDiscountLine(models.Model):
    _name = "product.quantity.auto.discount.line"

    product_id = fields.Many2one(
        "product.product", required=True, ondelete="cascade", string="Product"
    )
    qty_min = fields.Integer(
        required=True,
        string="Minimum Quantity",
        help="If quantity falls between min and max, the discount will be applied",
    )
    qty_max = fields.Integer(
        required=True,
        string="Maximum Quantity",
        help="If quantity falls between min and max, the discount will be applied",
    )
    discount_percentage = fields.Float(
        string="Discount (%)", digits="Discount", required=True
    )

    @api.constrains("qty_min", "qty_max", "discount_percentage", "product_id")
    def _check_constraints(self):
        # Check for any misconfigured discounts
        for record in self:
            if not (0 <= record.discount_percentage <= 100):
                raise ValidationError(
                    _("Discount percentage must be between 0 and 100.")
                )
            if record.qty_max < record.qty_min:
                raise ValidationError(
                    _("Maximum quantity can't be less than minimum quantity")
                )
            overlaps = self.search(
                [
                    ("product_id", "=", record.product_id.id),
                    ("id", "!=", record.id),
                    ("qty_min", "<=", record.qty_max),
                    ("qty_max", ">=", record.qty_min),
                ]
            )
            if overlaps:
                raise ValidationError(
                    _("Discount quantity ranges must not overlap for the same product.")
                )
