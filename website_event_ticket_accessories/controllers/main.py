import logging

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteEventTicketAccessoriesSaleController(WebsiteSale):
    _ticket_accessories_force_cart_key = "ticket_accessories_cart_forced_order_id"

    def _clear_ticket_accessories_force_cart_session(self):
        request.session.pop(self._ticket_accessories_force_cart_key, None)

    def _get_ticket_accessory_products(self, order_sudo):
        if not order_sudo:
            return request.env["product.product"]

        return order_sudo._get_ticket_accessory_products()

    def _order_has_ticket_accessories(self, order_sudo):
        return bool(self._get_ticket_accessory_products(order_sudo))

    def _cart_values(self, **post):
        values = super()._cart_values(**post)

        order_sudo = request.website.sale_get_order()
        accessory_products = self._get_ticket_accessory_products(order_sudo)

        if accessory_products:
            values["suggested_products"] = (
                values.get("suggested_products", request.env["product.product"])
                | accessory_products
            )

        return values

    @http.route(
        ["/shop/cart"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def cart(self, access_token=None, revive="", **post):
        order_sudo = request.website.sale_get_order()

        if not order_sudo or not order_sudo.cart_quantity:
            self._clear_ticket_accessories_force_cart_session()

        return super().cart(access_token=access_token, revive=revive, **post)

    @http.route(
        ["/shop/cart/clear"],
        type="json",
        auth="public",
        website=True,
    )
    def clear_cart(self):
        self._clear_ticket_accessories_force_cart_session()
        return super().clear_cart()

    @http.route(
        ["/shop/checkout"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def checkout(self, **post):
        order_sudo = request.website.sale_get_order()

        if (
            not order_sudo
            or order_sudo.state != "draft"
            or not order_sudo.cart_quantity
        ):
            self._clear_ticket_accessories_force_cart_session()
            return super().checkout(**post)

        forced_order_id = request.session.get(self._ticket_accessories_force_cart_key)

        if (
            self._order_has_ticket_accessories(order_sudo)
            and forced_order_id != order_sudo.id
        ):
            request.session[self._ticket_accessories_force_cart_key] = order_sudo.id
            request.session["sale_last_order_id"] = order_sudo.id
            return request.redirect("/shop/cart")

        return super().checkout(**post)
