from odoo import api, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.model_create_multi
    def create(self, vals_list):
        registrations = super().create(vals_list)
        registrations.filtered(
            lambda registration: registration.state == "open"
        )._reject_other_registrations()
        return registrations

    def write(self, vals):
        res = super().write(vals)
        if vals.get("state") == "open":
            self._reject_other_registrations()
        return res

    def _reject_other_registrations(self):
        """Cancel the unconfirmed registrations of the same participant and test type
        when a registration gets confirmed."""
        for registration in self:
            # sudo: the registrations of the same participant are cancelled even
            # if the user who confirms cannot see them
            other_registrations = self.sudo().search(
                [
                    ("id", "!=", registration.id),
                    ("partner_id", "=", registration.partner_id.id),
                    (
                        "registration_partner_id",
                        "=",
                        registration.registration_partner_id.id,
                    ),
                    (
                        "registration_survey_id",
                        "in",
                        registration.event_id.survey_ids.ids,
                    ),
                    ("state", "=", "draft"),
                ]
            )
            other_registrations.write({"state": "cancel"})
