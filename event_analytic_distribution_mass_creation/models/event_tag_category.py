from odoo import fields, models


class EventTagCategory(models.Model):
    _inherit = "event.tag.category"

    use_in_analytic_accounting_rules = fields.Boolean(
        string="Use in Analytic Accounting Rules",
        help="Allow selecting the tags of this category in the event analytic "
        "accounting rules of ticket products",
    )
