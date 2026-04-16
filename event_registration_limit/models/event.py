import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.model_create_multi
    def create(self, vals_list):
        registrations = super(EventRegistration, self).create(vals_list)
        for registration in registrations:
            if registration.state == "open":
                self._reject_other_registrations(registration)

        return registrations

    def write(self, vals):
        """Tarkistaa, onko ilmoittautuminen vahvistettu ja hylkää muut
        saman koetyypin ilmoittautumiset."""
        confirming = vals.get("state") == "open"
        ret = super(EventRegistration, self).write(vals)
        if confirming:
            for registration in self:
                self._reject_other_registrations(registration)

        return ret

    def _reject_other_registrations(self, confirmed_registration):
        """Hylkää muut ilmoittautumiset saman koetyypin perusteella."""
        _logger.info(
            "CHECK CANCEL: confirmed id=%s partner_id=%s registration_partner_id=%s survey=%s event=%s",  # NOQA
            confirmed_registration.id,
            confirmed_registration.partner_id.id,
            confirmed_registration.registration_partner_id.id,
            confirmed_registration.registration_survey_id.id,
            confirmed_registration.event_id.id,
        )
        other_registrations = (
            self.env["event.registration"]
            .sudo()
            .search(
                [
                    ("id", "!=", confirmed_registration.id),
                    ("partner_id", "=", confirmed_registration.partner_id.id),
                    (
                        "registration_partner_id",
                        "=",
                        confirmed_registration.registration_partner_id.id,
                    ),
                    (
                        "registration_survey_id",
                        "in",
                        confirmed_registration.event_id.survey_ids.ids,
                    ),
                    ("state", "in", ["draft"]),
                ]
            )
        )
        _logger.info(
            "CANCELLING IDS for confirmed %s: %s",
            confirmed_registration.id,
            other_registrations.ids,
        )
        other_registrations.write({"state": "cancel"})
