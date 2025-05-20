from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_qty_autodiscount_line_ids = fields.One2many(
        "product.quantity.auto.discount.line",
        compute="_compute_product_qty_autodiscount_line_ids",
        inverse="_inverse_product_qty_autodiscount_line_ids",
        string="Quantity-based Automatic Discounts",
        help="Discounts to automatically apply when ordering tickets via website",
    )

    @api.depends("product_variant_ids.product_qty_autodiscount_line_ids")
    def _compute_product_qty_autodiscount_line_ids(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_qty_autodiscount_line_ids = (
                    template.product_variant_ids.product_qty_autodiscount_line_ids
                )
            else:
                template.product_qty_autodiscount_line_ids = False

    def _inverse_product_qty_autodiscount_line_ids(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.product_qty_autodiscount_line_ids = (
                    template.product_qty_autodiscount_line_ids
                )
