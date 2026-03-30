import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _init_registrations(self):
        # Custom handling for when Sale Order is confirmed:
        # If confirming happened specifically via Sale Order's confirm
        """Create registrations linked to a sales order line. A sale
        order line has a product_uom_qty attribute that will be the number of
        registrations linked to this line."""

        if not self.order_id.create_event_registrations_as_drafts:
            # Default core functionality
            return super()._init_registrations()
        else:
            # Custom handling - only change is that state gets
            # explicitly set to draft, instead of letting it default to open.
            registrations_vals = []
            for so_line in self:
                if not so_line.product_type == "event":
                    continue

                for _count in range(
                    int(so_line.product_uom_qty) - len(so_line.registration_ids)
                ):
                    values = {
                        "sale_order_line_id": so_line.id,
                        "sale_order_id": so_line.order_id.id,
                        "state": "draft",
                    }
                    registrations_vals.append(values)

            if registrations_vals:
                self.env["event.registration"].sudo().create(registrations_vals)
            return True
