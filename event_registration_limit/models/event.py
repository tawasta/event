from odoo import api, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.model_create_multi
    def create(self, vals_list):
        """Hylkää muut saman koetyypin ilmoittautumiset, kun yksi vahvistetaan."""
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
        other_registrations = (
            self.env["event.registration"]
            .sudo()
            .search(
                [
                    ("id", "!=", confirmed_registration.id),
                    ("partner_id", "=", confirmed_registration.partner_id.id),
                    (
                        "registration_survey_id",
                        "in",
                        confirmed_registration.event_id.survey_ids.ids,
                    ),
                    ("state", "in", ["draft"]),
                ]
            )
        )
        other_registrations.write({"state": "cancel"})
