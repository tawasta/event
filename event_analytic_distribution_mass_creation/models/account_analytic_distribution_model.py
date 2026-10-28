from odoo import fields, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    generated_from_event_rules = fields.Boolean(
        string="Generated from Event Rules",
        copy=False,
        help="Created from the event analytic accounting rules of the ticket "
        "products. Generating analytic distributions on the event keeps this "
        "model up to date. Untick to keep manual changes.",
    )
