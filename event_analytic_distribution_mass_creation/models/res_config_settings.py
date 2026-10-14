from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    event_analytic_account_creation = fields.Boolean(
        string="Create Event Analytic Accounts",
        config_parameter="event_analytic_distribution_mass_creation"
        ".create_event_analytic_account",
        help="When analytic distributions are generated for an event, also create "
        "an analytic account for the event and allocate the tickets to it",
    )
    event_analytic_account_plan_id = fields.Many2one(
        "account.analytic.plan",
        string="Event Analytic Plan",
        config_parameter="event_analytic_distribution_mass_creation"
        ".event_analytic_plan_id",
        help="Plan of the event analytic accounts. It must differ from the plans "
        "of the analytic accounts used in the rules of ticket products.",
    )
