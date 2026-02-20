import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Overrides
    # -------------------------------------------------------------------------

    # def action_confirm(self):
    #     """Set the recap email request flag when a registration is confirmed."""
    #     res = super().action_confirm()
    #     self.write({"survey_answer_recap_email_requested": True})
    #     return res

    def write(self, vals):
        """Override write to flag registrations for recap email on confirmation.

        We intercept state changes here rather than in ``action_confirm()``
        because registrations can reach the 'open' state through multiple
        paths (e.g. the state widget on the form view).

        The inner write uses ``super()`` directly to avoid recursion — if we
        called ``self.write()`` it would re-enter this override and evaluate
        the ``state`` check again unnecessarily.
        """
        res = super().write(vals)
        if vals.get("state") == "open":
            to_flag = self.filtered(
                lambda reg: not reg.survey_answer_recap_email_requested
            )
            if to_flag:
                super(EventRegistration, to_flag).write(
                    {"survey_answer_recap_email_requested": True}
                )
        return res

    # -------------------------------------------------------------------------
    # Cron
    # -------------------------------------------------------------------------

    def _cron_send_survey_recap_emails(self):
        """Called by ir.cron. Find eligible registrations and send emails."""

        _logger.info("Running survey recap")
        candidates = self.search(self._get_survey_recap_email_domain())
        if not candidates:
            return

        _logger.info("found candidates:")
        _logger.info(candidates)

        eligible = candidates._filter_survey_recap_eligible()
        if not eligible:
            return

        _logger.info("filtered eligibles:")
        _logger.info(eligible)

        _logger.info(
            "Sending survey recap email for %d registration(s): %s",
            len(eligible),
            eligible.ids,
        )
        eligible._send_survey_recap_email()

    # -------------------------------------------------------------------------
    # Domain & filtering helpers
    # -------------------------------------------------------------------------

    @api.model
    def _get_survey_recap_email_domain(self):
        """Return the search domain for candidate registrations.

        Pushes as many criteria as possible into SQL so the Python-level
        eligibility check only processes a small set.
        """
        return [
            ("state", "=", "open"),
            ("survey_answer_recap_email_requested", "=", True),
            ("survey_answer_recap_email_sent", "=", False),
            ("event_id.stage_id.pipe_end", "=", False),
            ("event_id.stage_id.cancel", "=", False),
        ]

    def _filter_survey_recap_eligible(self):
        """Return the subset of ``self`` where all expected surveys are answered.

        An event registration is eligible when every ``survey.survey`` in
        ``event_id.survey_ids`` has at least one corresponding record in
        ``survey_answer_ids`` (i.e. the answered surveys are a superset of
        the expected surveys).

        Only completed survey inputs (``state == 'done'``) are considered.
        Inputs still in progress are ignored.

        Registrations whose event has **no** linked surveys are skipped
        because there is nothing to recap.
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

    # -------------------------------------------------------------------------
    # Email sending
    # -------------------------------------------------------------------------

    def _send_survey_recap_email(self):
        """Send the survey recap email for each registration in ``self``."""
        template = self.env.ref(
            "event_registration_survey_recap_mail_after_registration"
            ".mail_template_event_registration_survey_recap",
            raise_if_not_found=True,
        )
        for registration in self:
            try:
                template.send_mail(
                    registration.id,
                    force_send=False,
                    raise_exception=False,
                )

                registration.survey_answer_recap_email_sent = fields.Datetime.now()
                registration.message_post(
                    body=_("Sent survey answer recap to registrant"),
                )

                _logger.debug(
                    "Survey recap email queued for registration %s (id=%d)",
                    registration.display_name,
                    registration.id,
                )

            except Exception:
                _logger.exception(
                    "Failed to queue survey recap email for " "registration %s (id=%d)",
                    registration.display_name,
                    registration.id,
                )
                continue
