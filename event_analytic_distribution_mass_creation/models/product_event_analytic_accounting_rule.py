from odoo import fields, models


class ProductEventAnalyticAccountingRule(models.Model):
    _name = "product.event.analytic.accounting.rule"
    _description = "Product Event Analytic Accounting Rule"

    product_id = fields.Many2one(
        "product.product",
        required=True,
        ondelete="cascade",
        index=True,
        domain=[("detailed_type", "=", "event")],
    )
    event_tag_id = fields.Many2one(
        "event.tag",
        required=True,
        ondelete="cascade",
        domain=[("category_id.use_in_analytic_accounting_rules", "=", True)],
        help="The rule is used for events that have this tag",
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        required=True,
        ondelete="restrict",
        help="Analytic account for the tickets that are sold with this product "
        "in the events that have the tag",
    )
    comment = fields.Char(help="Free text explanation of the rule")
    company_id = fields.Many2one(
        related="analytic_account_id.company_id",
        store=True,
    )

    _sql_constraints = [
        (
            "product_event_tag_unique",
            "unique(product_id, event_tag_id)",
            "An event tag can be used only on one line per product.",
        ),
    ]
