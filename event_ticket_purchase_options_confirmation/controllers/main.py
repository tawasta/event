from werkzeug.urls import url_encode

from odoo.http import request
from odoo.tools import is_html_empty

from odoo.addons.website_sale.controllers.main import WebsiteSale

REGISTRATIONS_PAGE_URL = "/my/events"


class WebsiteSaleEventRegistrations(WebsiteSale):
    def _prepare_shop_payment_confirmation_values(self, order):
        values = super()._prepare_shop_payment_confirmation_values(order)
        registrations = order.order_line.registration_ids.filtered(
            lambda registration: registration.state != "cancel"
        )
        if not registrations:
            return values

        help_text = request.website.event_invitation_confirmation_help
        values["event_registrations"] = {
            "help": False if is_html_empty(help_text) else help_text,
            # The registrations page lists no draft registrations, and
            # invitations can be sent only for confirmed ones. Free tickets are
            # confirmed before the payment, so all must be confirmed.
            "is_confirmed": all(
                state in ("open", "done") for state in registrations.mapped("state")
            ),
            **self._get_event_registrations_access(order),
        }
        return values

    def _get_event_registrations_access(self, order):
        """Return the URL that takes the buyer to the registrations page, and
        whether the buyer must log in or sign up on the way.

        A guest buyer can reach the page only through the account of the order
        customer. A customer with an account logs in, and a customer without
        one gets the same signup link that core offers on this page, with the
        registrations page as the redirect.
        """
        if not request.website.is_public_user():
            return {"url": REGISTRATIONS_PAGE_URL, "access": "portal"}

        partner = order.partner_id
        if partner.user_ids:
            # No signup token: it would let the guest set the password of an
            # existing account
            query = url_encode({"redirect": REGISTRATIONS_PAGE_URL})
            return {"url": f"/web/login?{query}", "access": "login"}

        if request.env["res.users"]._get_signup_invitation_scope() != "b2c":
            return {}

        signup_urls = partner.with_context(
            relative_url=True, signup_valid=True
        )._get_signup_url_for_action(url=REGISTRATIONS_PAGE_URL)
        return {"url": signup_urls[partner.id], "access": "signup"}
