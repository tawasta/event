from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def unlink(self):
        if (
            self.env["event.registration"].search_count(
                [("sale_order_id", "in", self.ids)]
            )
            > 0
        ):
            raise UserError(
                _("Cannot delete Sale Orders with associated event registrations.")
            )
        else:
            return super(SaleOrder, self).unlink()


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def unlink(self):
        registration_count = self.env["event.registration"].search_count(
            [("sale_order_line_id", "in", self.ids)]
        )
        if registration_count > 0:
            raise UserError(
                _("Cannot delete Sale Order Lines with associated event registrations.")
            )
        else:
            return super(SaleOrderLine, self).unlink()
