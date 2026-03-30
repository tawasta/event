from odoo import api, fields, models


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    save_as_event_registration_company_name = fields.Boolean(
        "Save as Event Registration's Company Name",
        compute="_compute_save_as_event_registration_company_name",
        readonly=False,
        store=True,
        copy=True,
        help="If checked, the user's answer is saved into the related "
        "event registration's company name field.",
    )

    @api.depends("question_type")
    def _compute_save_as_event_registration_company_name(self):
        for question in self:
            if question.question_type != "char_box":
                question.save_as_event_registration_company_name = False
