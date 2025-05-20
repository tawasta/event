from odoo import fields, models, _
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    def sale_get_order(self, *args, **kwargs):
        # Write the discounts to SO lines
        res = super().sale_get_order(*args, **kwargs)

        self = self.with_company(self.company_id)
        SaleOrder = self.env["sale.order"].sudo()

        sale_order_id = request.session.get("sale_order_id")

        if sale_order_id:
            sale_order_sudo = SaleOrder.browse(sale_order_id).exists()

            for sale_order_line in sale_order_sudo.order_line:
                discount = sale_order_line._find_quantity_autodiscount()
                sale_order_line.write({"discount": discount})

        return res
