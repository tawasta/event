from werkzeug.urls import url_encode

from odoo.http import request, route

from odoo.addons.website_event_require_login.controllers.main import (
    RequireLoginToRegister,
)


class RequireLoginToConfirm(RequireLoginToRegister):
    @route()
    def registration_confirm(self, event, **post):
        """Refuse registrations of logged out users for login-only events.

        The page only hides the registration form from logged out users, so a
        stale page, an expired session or a direct POST could still reach this
        route. The check is done here, per request, so it cannot be bypassed.
        """
        if event.website_require_login and request.env.user._is_public():
            return request.redirect(
                "/web/login?%s" % url_encode({"redirect": event.website_url})
            )
        return super().registration_confirm(event, **post)
