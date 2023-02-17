from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    proposal_see_evaluation = fields.Boolean(
        string="The submitter of the proposal can see the evaluations",
        config_parameter="website_event_track_advanced.proposal_see_evaluation",
    )
