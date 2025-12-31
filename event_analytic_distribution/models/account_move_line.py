import logging

from odoo import api, models
from odoo.tools import frozendict

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends(
        "account_id",
        "partner_id",
        "product_id",
        "sale_line_ids",
        "sale_line_ids.event_id",
        "sale_line_ids.event_ticket_id",
    )
    def _compute_analytic_distribution(self):
        cache = {}
        for line in self:
            if line.display_type == "product" or not line.move_id.is_invoice(
                include_receipts=True
            ):
                arguments = frozendict(
                    {
                        "product_id": line.product_id.id,
                        "product_categ_id": line.product_id.categ_id.id,
                        "partner_id": line.partner_id.id,
                        "partner_category_id": line.partner_id.category_id.ids,
                        "account_prefix": line.account_id.code,
                        "company_id": line.company_id.id,
                        # Invoice lines do not have event info, but the related
                        # SO lines do. Attempt to fetch it from there. If the
                        # invoice line <-> SO line connections have been
                        # manually altered by user, this may not always yield results
                        # though.
                        "event_id": (
                            line.sale_line_ids
                            and line.sale_line_ids[0].event_id
                            and line.sale_line_ids
                            and line.sale_line_ids[0].event_id.id
                            or False
                        ),
                        "event_ticket_id": (
                            line.sale_line_ids
                            and line.sale_line_ids[0].event_ticket_id
                            and line.sale_line_ids[0].event_ticket_id.id
                            or False
                        ),
                    }
                )
                if arguments not in cache:
                    cache[arguments] = self.env[
                        "account.analytic.distribution.model"
                    ]._get_distribution(arguments)
                line.analytic_distribution = (
                    cache[arguments] or line.analytic_distribution
                )
