from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteEventCartSuggestedEventsController(WebsiteSale):
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
