from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_sale_order_line_multiline_description_sale(self):
        """
        Add registrant to SO line description
        """
        res = super()._get_sale_order_line_multiline_description_sale()

        domain = [("sale_order_line_id", "=", self.id), ("state", "!=", "cancel")]
        registrations = self.env["event.registration"].sudo().search(domain)

        for registration in registrations:
            res += "\n" + registration.name

        return res
