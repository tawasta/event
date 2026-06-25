import logging

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


def _get_current_sale_order_id():
    """
    Return the ID of the current website sale order.

    The ID is used to bind the cart-page visit state to the active order.
    """
    order = request.website.sale_get_order()
    return order.id if order else None


def _is_successful_response(response):
    """
    Return True when the response is a successful 200 OK page render.

    Redirects, errors, and other non-200 responses must not mark the cart
    page as visited.
    """
    status_code = getattr(response, "status_code", None)

    if status_code is None:
        status_text = getattr(response, "status", "")
        try:
            status_code = int(str(status_text).split(" ", 1)[0])
        except Exception:
            status_code = None

    return status_code == 200


class WebsiteEventCartSuggestedEventsController(WebsiteSale):
    def _mark_cart_page_as_visited_for_current_order(self):
        """
        Store that the cart page has been visited for the current sale order.

        The visit state is tied to the active order so it cannot be reused
        for another checkout flow or another sale order.
        """
        sale_order_id = _get_current_sale_order_id()

        if sale_order_id:
            request.session["website_sale_cart_page_visited"] = True
            request.session["website_sale_cart_page_visited_order_id"] = sale_order_id

    def _has_cart_page_been_visited_for_current_order(self):
        """
        Return whether the cart page has been visited for the current order.

        The stored sale order ID must match the active sale order ID.
        """
        sale_order_id = _get_current_sale_order_id()

        return (
            request.session.get("website_sale_cart_page_visited") is True
            and request.session.get("website_sale_cart_page_visited_order_id")
            == sale_order_id
        )

    def _ensure_cart_page_visited_before_checkout_step(self):
        """
        Ensure that the cart page has been visited before checkout steps.

        If the cart page has not been visited for the current sale order,
        redirect the user back to /shop/cart.
        """
        if not self._has_cart_page_been_visited_for_current_order():
            return request.redirect("/shop/cart")

        return None

    def _clear_cart_page_visit_state(self):
        """
        Remove cart-page visit state from the current session.

        This prevents the state from affecting the next sale order.
        """
        request.session.pop("website_sale_cart_page_visited", None)
        request.session.pop("website_sale_cart_page_visited_order_id", None)

    @http.route()
    def cart(self, access_token=None, revive="", **post):
        """
        Once the cart page is successfully rendered, mark it as visited for
        the current sale order.
        """
        response = super().cart(
            access_token=access_token,
            revive=revive,
            **post
        )

        is_get_request = request.httprequest.method == "GET"
        is_xhr_request = bool(post.get("xhr"))

        if is_get_request and not is_xhr_request and _is_successful_response(response):
            self._mark_cart_page_as_visited_for_current_order()

        return response

    @http.route()
    def address(self, **post):
        """
        Override the address page.

        Require the cart page to have been visited before the address page
        can be accessed or submitted.
        """
        redirect_response = self._ensure_cart_page_visited_before_checkout_step()
        if redirect_response:
            return redirect_response

        is_post_request = request.httprequest.method == "POST"

        if is_post_request:
            post = dict(post)
            post.setdefault("callback", "/shop/checkout")

        return super().address(**post)

    @http.route()
    def checkout(self, **post):
        """
        Require the cart page to have been visited before checkout can be
        accessed.
        """
        redirect_response = self._ensure_cart_page_visited_before_checkout_step()
        if redirect_response:
            return redirect_response

        return super().checkout(**post)

    @http.route()
    def confirm_order(self, **post):
        """
        Require the cart page to have been visited before order confirmation.
        """
        redirect_response = self._ensure_cart_page_visited_before_checkout_step()
        if redirect_response:
            return redirect_response

        return super().confirm_order(**post)

    @http.route()
    def shop_payment(self, **post):
        """
        Require the cart page to have been visited before payment can be
        accessed.
        """
        redirect_response = self._ensure_cart_page_visited_before_checkout_step()
        if redirect_response:
            return redirect_response

        return super().shop_payment(**post)

    @http.route()
    def shop_payment_confirmation(self, **post):
        """
        Clear the cart-page visit state after the checkout flow has reached
        payment confirmation.
        """
        response = super().shop_payment_confirmation(**post)

        self._clear_cart_page_visit_state()

        return response

    def _get_cart_suggested_events(self, order_sudo):
        if not order_sudo:
            return request.env["event.event"]

        ticket_lines = order_sudo.order_line.filtered(
            lambda line: line.event_id or line.event_ticket_id
        )
        if not ticket_lines:
            return request.env["event.event"]

        cart_event_ids = ticket_lines.mapped("event_id").ids
        cart_event_ids += ticket_lines.mapped("event_ticket_id.event_id").ids

        cart_events = request.env["event.event"].sudo().browse(cart_event_ids).exists()

        suggested_events = cart_events.mapped("cart_suggested_event_ids")

        return suggested_events.filtered(
            lambda event: event.website_published
            and event.event_registrations_open
            and event.id not in cart_event_ids
        )

    def _cart_values(self, **post):
        values = super()._cart_values(**post)

        order_sudo = request.website.sale_get_order()
        values["cart_suggested_event_ids"] = self._get_cart_suggested_events(order_sudo)

        return values