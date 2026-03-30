from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    survey_recap_email_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Survey Recap Email Template",
        domain=[("model_id.model", "=", "event.registration")],
        help="Email template sent to registrants once all survey answers "
        "have been processed. Leave empty to use the default template.",
        config_parameter="event_registration_survey_recap_mail_after_registration"
        ".default_survey_recap_email_template_id",
    )
