from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventRegistrationLimitController(WebsiteEventController):
    def _prepare_event_register_values(self, event, **post):
        values = super()._prepare_event_register_values(event, **post)
        values.update(self._get_registration_limit_values(event))
        return values

    def _get_registration_limit_values(self, event):
        """Tell whether the user can still register a dog to the tests of the event."""
        user_dogs = request.env.user.partner_id.my_dog_ids
        if not user_dogs:
            return {
                "registration_disabled": True,
                "error_message": request.env._("You have no dogs added."),
            }
        # sudo: the registrations of the user's dogs may belong to other contacts
        existing_registrations = (
            request.env["event.registration"]
            .sudo()
            .search(
                [
                    ("registration_survey_id", "in", event.sudo().survey_ids.ids),
                    ("registration_partner_id", "in", user_dogs.ids),
                    ("state", "=", "open"),
                    ("event_id.stage_id.pipe_end", "=", False),
                ]
            )
        )
        registered_dogs = existing_registrations.registration_partner_id
        if user_dogs <= registered_dogs:
            return {
                "registration_disabled": True,
                "error_message": request.env._(
                    "All your dogs are already registered for this test type. "
                    "Please wait for the evaluation before registering again."
                ),
            }
        return {"registration_disabled": False, "error_message": ""}
