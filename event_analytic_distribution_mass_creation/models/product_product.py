from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_event_analytic_accounting_rule_ids = fields.One2many(
        "product.event.analytic.accounting.rule",
        "product_id",
        string="Event Analytic Accounting Rules",
        help="Analytic accounts to use for the tickets of this product, "
        "based on the tags of the event",
    )
