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
        compute="_compute_available_surveys",
        readonly=True,
    )

    @api.depends("event_registration_id")
    def _compute_available_surveys(self):
        for wizard in self:
            wizard.available_survey_ids = (
                wizard.event_registration_id.event_id.survey_ids
            )

    def action_create_answer_for_survey(self):
        self.ensure_one()

        registration = self.event_registration_id

        partner = registration.partner_id
        # TODO attendee partner may be missing if creating from SO
        # partner = registration.attendee_partner_id

        selected_survey = self.survey_to_answer_id

        if not partner:
            raise UserError(_("This registration has no attendee partner set."))

        # society_event_core keeps the answers in the original stage when answers
        # come in via website, do the same here. # TODO not working yet?
        # earliest_stage = self.env["survey.user_input.stage"].search(
        #     domain=[("is_editable", "=", True)], order="sequence ASC", limit="1"
        # )

        # _logger.info("stage: %s", earliest_stage)

        # Create a participation record for the selected survey and update some
        # values for it
        placeholder_user_input_id = selected_survey._create_answer(
            partner=partner, check_attempts=False
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
                # "stage_id": earliest_stage[0].id,  # TODO: not working?
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
