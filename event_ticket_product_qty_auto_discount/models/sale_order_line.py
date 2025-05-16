from odoo import models, api

import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _find_quantity_autodiscount(self):
        # Find the discount that matches the quantity of tickets in the cart SO line

        self.ensure_one()

        autodiscount = 0

        for autodiscount_line_id in self.product_id.product_qty_autodiscount_line_ids:
            if (
                autodiscount_line_id.qty_min
                <= self.product_uom_qty
                <= autodiscount_line_id.qty_max
            ):
                autodiscount = autodiscount_line_id.discount_percentage
                break

        return autodiscount
