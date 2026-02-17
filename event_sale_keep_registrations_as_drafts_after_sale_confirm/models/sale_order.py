from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    create_event_registrations_as_drafts = fields.Boolean(
        default=False,
        copy=False,
        help="When the sale is confirmed, any event registrations will be kept in "
        "draft state instead of confirming them.",
    )
