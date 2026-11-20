from odoo.http import request
from odoo.tools import is_html_empty

from odoo.addons.website_sale.controllers.main import WebsiteSale

INVITATION_PAGE_URL = "/my/events"


class WebsiteSaleEventInvitation(WebsiteSale):
    def _prepare_shop_payment_confirmation_values(self, order):
        values = super()._prepare_shop_payment_confirmation_values(order)
        invite_registrations = order.order_line.registration_ids.filtered(
            "invite_others"
        )
        if not invite_registrations:
            return values

        help_text = request.website.event_invitation_confirmation_help
        values["event_invitation"] = {
            "help": False if is_html_empty(help_text) else help_text,
            # Invitations can be sent only for confirmed registrations, and the
            # invitation page lists no draft ones
            "is_confirmed": any(
                state in ("open", "done")
                for state in invite_registrations.mapped("state")
            ),
            **self._get_event_invitation_access(order),
        }
        return values

    def _get_event_invitation_access(self, order):
        """Return the URL that takes the buyer to the invitation page, and
        whether the buyer must log in or sign up on the way.

        A guest buyer can reach the page only through the account of the order
        customer, so the same signup link that core offers on this page is
        used, with the invitation page as the redirect.
        """
        if not request.website.is_public_user():
            return {"url": INVITATION_PAGE_URL, "access": "portal"}

        partner = order.partner_id
        has_account = bool(partner.user_ids)
        signup_allowed = (
            request.env["res.users"]._get_signup_invitation_scope() == "b2c"
        )
        if not has_account and not signup_allowed:
            return {}

        signup_urls = partner.with_context(
            relative_url=True, signup_valid=True
        )._get_signup_url_for_action(url=INVITATION_PAGE_URL)
        return {
            "url": signup_urls[partner.id],
            "access": "login" if has_account else "signup",
        }
