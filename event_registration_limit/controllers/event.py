from odoo import http
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.http import request


class CustomWebsiteEventRegistrationController(WebsiteEventController):
    @http.route()
    def event_register(self, event, **post):
        partner = request.env.user.partner_id if request.env.user else False
        registration_disabled = False
        error_message = ""

        if partner:
            user_dog_ids = partner.my_dog_ids.ids

            if user_dog_ids:
                existing_registrations = (
                    request.env["event.registration"]
                    .sudo()
                    .search(
                        [
                            (
                                "registration_survey_id",
                                "in",
                                event.sudo().survey_ids.ids,
                            ),
                            (
                                "registration_partner_id",
                                "in",
                                user_dog_ids,
                            ),
                            ("state", "in", ["open"]),
                            ("event_id.stage_id.pipe_end", "=", False),
                        ]
                    )
                )

                registered_dog_ids = set(
                    existing_registrations.mapped("registration_partner_id").ids
                )

                if set(user_dog_ids).issubset(registered_dog_ids):
                    registration_disabled = True
                    error_message = (
                        "Kaikki koirasi ovat jo ilmoittautuneet tähän "
                        "koetyyppiin. Odota arviointia ennen uutta "
                        "ilmoittautumista."
                    )
            else:
                registration_disabled = True
                error_message = "Sinulla ei ole koiria lisättynä."

        values = super(CustomWebsiteEventRegistrationController, self).event_register(
            event, **post
        )

        values.qcontext.update(
            {
                "registration_disabled": registration_disabled,
                "error_message": error_message,
            }
        )
        return values
