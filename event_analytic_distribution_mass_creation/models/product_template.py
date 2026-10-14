from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_event_analytic_accounting_rule_ids = fields.One2many(
        "product.event.analytic.accounting.rule",
        compute="_compute_product_event_analytic_accounting_rule_ids",
        inverse="_inverse_product_event_analytic_accounting_rule_ids",
        string="Event Analytic Accounting Rules",
        help="Analytic accounts to use for the tickets of this product, "
        "based on the tags of the event",
    )

    def _get_related_fields_variant_template(self):
        """Apply rules entered on a new product after core has created its variant."""
        related_fields = super()._get_related_fields_variant_template()
        related_fields.append("product_event_analytic_accounting_rule_ids")
        return related_fields

    @api.depends("product_variant_ids.product_event_analytic_accounting_rule_ids")
    def _compute_product_event_analytic_accounting_rule_ids(self):
        """Show the rules of a single-variant product on the product template form."""
        for template in self:
            if len(template.product_variant_ids) == 1:
                variant = template.product_variant_ids
                template.product_event_analytic_accounting_rule_ids = (
                    variant.product_event_analytic_accounting_rule_ids
                )
            else:
                template.product_event_analytic_accounting_rule_ids = False

    def _inverse_product_event_analytic_accounting_rule_ids(self):
        """Store the rules edited on the product template form to its only variant."""
        for template in self:
            if len(template.product_variant_ids) == 1:
                variant = template.product_variant_ids
                variant.product_event_analytic_accounting_rule_ids = (
                    template.product_event_analytic_accounting_rule_ids
                )
