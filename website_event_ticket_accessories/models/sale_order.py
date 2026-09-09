from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_ticket_accessory_products(self):
        """Accessory products suggested by the event tickets already in
        this order's cart, excluding anything already added."""
        self.ensure_one()

        ticket_lines = self.website_order_line.filtered("event_ticket_id")
        if not ticket_lines:
            return self.env["product.product"]

        cart_product_ids = set(self.website_order_line.product_id.ids)

        return ticket_lines.event_ticket_id.mapped("accessory_product_ids").filtered(
            lambda product: product.id not in cart_product_ids
            and product.sale_ok
            and product._is_add_to_cart_allowed()
        )

    def _cart_accessories(self):
        """Core only calls _cart_accessories() (not the controller's
        _cart_values()) when re-rendering the cart lines after an AJAX
        add-to-cart, so without this override the ticket accessories
        disappear from view until a full page reload."""
        return super()._cart_accessories() | self._get_ticket_accessory_products()
