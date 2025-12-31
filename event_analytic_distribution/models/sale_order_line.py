import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.partner_id", "product_id", "event_id", "event_ticket_id")
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type:
                distribution = line.env[
                    "account.analytic.distribution.model"
                ]._get_distribution(
                    {
                        "product_id": line.product_id.id,
                        "product_categ_id": line.product_id.categ_id.id,
                        "partner_id": line.order_id.partner_id.id,
                        "partner_category_id": line.order_id.partner_id.category_id.ids,
                        "company_id": line.company_id.id,
                        "event_id": line.event_id and line.event_id.id or False,
                        "event_ticket_id": line.event_ticket_id
                        and line.event_ticket_id.id
                        or False,
                    }
                )
                line.analytic_distribution = distribution or line.analytic_distribution
