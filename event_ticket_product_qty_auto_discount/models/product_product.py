from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_qty_autodiscount_line_ids = fields.One2many(
        "product.quantity.auto.discount.line",
        "product_id",
        string="Quantity-Based Automatic Discounts",
        help="Discounts to automatically apply when ordering tickets via website",
    )
