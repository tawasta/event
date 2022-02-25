from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    batch_id = fields.Many2one(string="Batch", comodel_name="op.batch")
