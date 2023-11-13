from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    proposal_see_evaluation = fields.Boolean(
        string="The submitter of the proposal can see the evaluations",
        config_parameter="website_event_track_advanced.proposal_see_evaluation",
    )

    evaluator_see_attachments = fields.Boolean(
        string="Evaluator persons can see the attachments",
        config_parameter="website_event_track_advanced.evaluator_see_attachments",
    )
