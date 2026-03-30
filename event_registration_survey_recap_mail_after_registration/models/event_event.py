from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    send_survey_recap_to_registrants = fields.Boolean(
        string="Send Survey Recap to Registrants",
        default=False,
        copy=False,
        help=(
            "When enabled, a survey answer recap email is sent to future registrants "
            "once all linked survey answers have been processed."
        ),
    )
