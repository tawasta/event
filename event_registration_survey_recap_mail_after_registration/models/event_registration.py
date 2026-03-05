import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    survey_answer_recap_email_requested = fields.Boolean(
        string="Survey Recap Email Requested",
        default=False,
        copy=False,
        help=(
            "Set to True when the registration is confirmed and a recap "
            "email should be sent once all survey answers are available."
        ),
    )
    survey_answer_recap_email_sent = fields.Datetime(
        string="Survey Recap Email Sent On",
        copy=False,
        readonly=True,
        help=(
            "Timestamp of when the survey recap email was sent. "
            "Populated automatically by the cron job."
        ),
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Flag new registrations for receiving a recap email, if
        the related event was configured to send them."""

        records = super().create(vals_list)
        to_flag = records.filtered(
            lambda reg: reg.event_id.send_survey_recap_to_registrants
        )

        if to_flag:
            super(EventRegistration, to_flag).write(
                {"survey_answer_recap_email_requested": True}
            )
        return records

    def _cron_send_survey_recap_emails(self):
        """Called by ir.cron. Find eligible registrations and send emails."""

        candidates = self.search(self._get_survey_recap_email_domain())
        if not candidates:
            return

        eligible = candidates._filter_survey_recap_eligible()
        if not eligible:
            return

        _logger.info(
            "Sending survey recap email for %d registration(s): %s",
            len(eligible),
            eligible.ids,
        )
        eligible._send_survey_recap_email()

    @api.model
    def _get_survey_recap_email_domain(self):
        """Return the search domain for candidate registrations."""
        return [
            ("state", "=", "open"),
            ("survey_answer_recap_email_requested", "=", True),
            ("survey_answer_recap_email_sent", "=", False),
            ("event_id.send_survey_recap_to_registrants", "=", True),
            ("event_id.stage_id.pipe_end", "=", False),
            ("event_id.stage_id.cancel", "=", False),
        ]

    def _filter_survey_recap_eligible(self):
        """Return the subset of ``self`` where all expected surveys are answered.

        An event registration is eligible when every survey.survey in
        event_id.survey_ids has at least one corresponding answer record in
        survey_answer_ids (i.e. the answered surveys are a superset of
        the expected surveys).

        Only completed survey inputs are considered. Registrations whose event has
        no linked surveys are skipped because there is nothing to recap.
        """
        eligible = self.browse()  # empty recordset
        for reg in self:
            expected_survey_ids = set(reg.event_id.survey_ids.ids)
            if not expected_survey_ids:
                # Nothing to recap — skip.
                continue
            completed_answers = reg.survey_answer_ids.filtered(
                lambda answer: answer.state == "done"
            )
            answered_survey_ids = set(completed_answers.mapped("survey_id").ids)
            if expected_survey_ids.issubset(answered_survey_ids):
                eligible |= reg
        return eligible

    def _get_survey_recap_email_template(self):
        """Return the mail template to use for the survey recap email.

        Reads the template configured in Settings > Events. Falls back to
        the default template shipped with this module if none is set.
        """
        configured_template_id = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "event_registration_survey_recap_mail_after_registration"
                ".default_survey_recap_email_template_id",
                default=0,
            )
        )
        if configured_template_id:
            template = self.env["mail.template"].browse(configured_template_id).exists()
            if template:
                return template
        return self.env.ref(
            "event_registration_survey_recap_mail_after_registration"
            ".mail_template_event_registration_survey_recap",
        )

    def _send_survey_recap_email(self):
        """Send the survey recap email for each registration in 'self'."""
        template = self._get_survey_recap_email_template()
        for registration in self:
            try:
                template.send_mail(
                    registration.id,
                    force_send=False,
                    raise_exception=False,
                )
            except Exception:
                _logger.exception(
                    "Failed to queue survey recap email for " "registration %s (id=%d)",
                    registration.display_name,
                    registration.id,
                )
                continue

            # Mark as sent to avoid future duplicate sending
            registration.survey_answer_recap_email_sent = fields.Datetime.now()
            _logger.debug(
                "Survey recap email queued for registration %s (id=%d)",
                registration.display_name,
                registration.id,
            )
