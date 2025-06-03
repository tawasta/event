from odoo import api, fields, models
from odoo.tools import float_is_zero


class EventRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
    confirmed_from_waiting_list = fields.Boolean(
        "Confirmed from waiting list", readonly=True, store=True
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends(
        "is_paid", "sale_order_id.currency_id", "sale_order_line_id.price_total"
    )
    def _compute_payment_status(self):
        for record in self:
            ticket = record.event_ticket_id
            so = record.sale_order_id
            so_line = record.sale_order_line_id
            if not so or float_is_zero(
                so_line.price_total, precision_digits=so.currency_id.rounding
            ):
                if not ticket or float_is_zero(ticket.price, precision_digits=2):
                    record.payment_status = "free"
                else:
                    record.payment_status = "to_pay"
            elif record.is_paid:
                record.payment_status = "paid"
            else:
                record.payment_status = "to_pay"

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
