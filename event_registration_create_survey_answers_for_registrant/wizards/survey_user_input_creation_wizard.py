import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SurveyUserInputCreationWizard(models.TransientModel):
    _name = "survey.user.input.creation.wizard"
    _description = "Survey User Input Creation Wizard"

    event_registration_id = fields.Many2one(
        "event.registration",
        required=True,
        readonly=True,
    )

    survey_to_answer_id = fields.Many2one(
        "survey.survey",
        string="Survey",
        required=True,
        domain="[('id', 'in', available_survey_ids)]",
    )

    available_survey_ids = fields.Many2many(
        "survey.survey",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        # Limit selectable surveys to just those that haven't been answered yet
        res = super().default_get(fields_list)
        reg_id = res.get("event_registration_id")
        if reg_id:
            registration = self.env["event.registration"].browse(reg_id)
            possible_surveys = registration.event_id.survey_ids
            answered_surveys = registration.survey_answer_ids.mapped("survey_id")
            res["available_survey_ids"] = (possible_surveys - answered_surveys).ids
        return res

    def action_create_answer_for_survey(self):
        # Create a placeholder survey user input records and launch the answering
        # view.
        self.ensure_one()

        registration = self.event_registration_id

        partner = registration.attendee_partner_id or registration.partner_id
        selected_survey = self.survey_to_answer_id

        if not partner:
            raise UserError(_("This registration has no partner information set."))

        # Create a participation record for the selected survey and update some
        # initial values for it
        placeholder_user_input_id = selected_survey._create_answer(
            partner=partner, check_attempts=False
        )

        # Clear the prefilled text questions' answers from any names, emails.
        # For some reason empty string can crash the launch of the answering view,
        # so just use dashes instead as a workaround...
        for survey_user_input_line in placeholder_user_input_id.user_input_line_ids:
            if survey_user_input_line.question_id.question_type == "char_box":
                placeholder_user_input_id._save_lines(
                    survey_user_input_line.question_id, "-"
                )

        placeholder_user_input_id.write(
            {
                # Add current user to contact_ids so that they have rights to
                # edit the survey
                "contact_ids": [(4, self.env.user.partner_id.id)],
                "created_on_behalf_of_registrant": True,
                "registration_id": self.event_registration_id.id,
                "event_id": self.event_registration_id.event_id.id,
                "event_ticket_id": (
                    self.event_registration_id.event_ticket_id
                    and self.event_registration_id.event_ticket_id.id
                    or False
                ),
            }
        )

        # Log some chatter notes to better see where the answers came from
        self.event_registration_id.message_post(
            body=_(
                "Survey '{survey_name}' participation created on behalf of an "
                "event registrant by {user}."
            ).format(
                survey_name=selected_survey.title,
                user=self.env.user.partner_id.name,
            )
        )

        placeholder_user_input_id.message_post(
            body=_(
                "Survey participation created on behalf of an "
                "event registrant by {user}."
            ).format(user=self.env.user.partner_id.name)
        )

        # Make the connection seen also from registration form
        self.event_registration_id.write(
            {"survey_answer_ids": [(4, placeholder_user_input_id.id)]}
        )

        # Open the core answering view in a new tab
        start_url = (
            f"/survey/edit/"
            f"{placeholder_user_input_id.survey_id.access_token}/"
            f"{placeholder_user_input_id.access_token}"
        )

        return {"type": "ir.actions.act_url", "url": start_url, "target": "new"}
