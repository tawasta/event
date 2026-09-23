import logging

from odoo import _
from odoo.exceptions import UserError
from odoo.http import request, route

from odoo.addons.website_event_sale.controllers.main import (
    WebsiteEventSaleController,
)

_logger = logging.getLogger(__name__)


class WebsiteEventSingleTicketController(WebsiteEventSaleController):
    def _get_cart_event_lines(self, event):
        """Find and return the current cart's SO lines for the given event"""
        order_sudo = request.website.sale_get_order()
        if not order_sudo or order_sudo.state != "draft":
            return request.env["sale.order.line"]
        return order_sudo.order_line.filtered(lambda line: line.event_id == event)

    def _prepare_event_register_values(self, event, **post):
        """Inject info about any existing cart lines for the same event"""
        values = super()._prepare_event_register_values(event, **post)
        values["cart_event_ticket_lines"] = self._get_cart_event_lines(event)
        return values

    @route()
    def registration_new(self, event, **post):
        """Add failsafe for checking for existing ticket in cart, if for some reason
        UI did not prevent the adding of 2nd ticket (e.g two registration page
        tabs open)"""
        if self._get_cart_event_lines(event):
            raise UserError(_("You already have a ticket for this event in your cart."))
        return super().registration_new(event, **post)

    @route()
    def registration_confirm(self, event, **post):
        """Add failsafe for checking for existing ticket in cart, if for some reason
        UI did not prevent the adding of 2nd ticket (e.g two registration page
        tabs open)"""
        # Check before super, which adds the ticket to the cart
        if self._get_cart_event_lines(event):
            return request.redirect(
                "/event/%s/register?registration_error_code=ticket_in_cart" % event.id
            )
        return super().registration_confirm(event, **post)
