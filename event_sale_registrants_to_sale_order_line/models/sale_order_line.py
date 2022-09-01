from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_sale_order_line_multiline_description_sale(self, product):
        """
        Add registrant to SO line description
        """
        res = super().get_sale_order_line_multiline_description_sale(product)

        domain = [("sale_order_line_id", "=", self.id), ("state", "!=", "cancel")]
        registrations = self.env["event.registration"].sudo().search(domain)

        for registration in registrations:
            res += "\n" + registration.name

        return res
