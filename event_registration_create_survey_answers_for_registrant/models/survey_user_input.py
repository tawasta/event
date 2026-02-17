import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    created_on_behalf_of_registrant = fields.Boolean(
        default=False,
        help="This participation's answers were filled in backend on behalf of the "
        "the registrant.",
    )
