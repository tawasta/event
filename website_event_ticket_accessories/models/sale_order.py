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
        """Both the /shop/cart page and the AJAX add-to-cart response
        build "suggested products" from this method directly, so without
        this override the ticket accessories would never show up there.

        Core returns a plain list (random.sample() of the recordset), not
        a recordset, so it has to be converted back before it can be
        combined with the ticket accessories."""
        core_accessories = self.env["product.product"].concat(
            *super()._cart_accessories()
        )
        return list(core_accessories | self._get_ticket_accessory_products())
