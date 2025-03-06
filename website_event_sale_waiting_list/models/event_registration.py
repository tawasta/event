##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models
from odoo.tools import float_is_zero

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


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
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for values in vals_list:
    #         # Add note with registration names
    #         if values.get("sale_order_id") and values.get("name"):
    #             sale_order = (
    #                 self.env["sale.order"].sudo().browse(values.get("sale_order_id"))
    #             )
    #             if sale_order.note:
    #                 new_note = sale_order.note + ", " + values.get("name")
    #             else:
    #                 new_note = values.get("name")
    #             sale_order.sudo().write({"note": new_note})
    #     registrations = super(EventRegistration, self).create(vals_list)
    #     return registrations

    # 7. Action methods
    # def _check_auto_confirmation(self):
    #     if self._context.get("skip_confirm") or self._context.get("skip_confirm_wait"):
    #         return False
    #     if any(
    #         not registration.event_id.auto_confirm
    #         or (
    #             registration.event_id.seats_available <= 0
    #             and registration.event_id.seats_limited
    #             or registration.event_ticket_id.seats_available <= 0
    #             and registration.event_ticket_id.seats_limited
    #         )
    #         or (
    #             registration.sale_order_id
    #             and registration.sale_order_id.state not in ["sent", "sale", "done"]
    #         )
    #         for registration in self
    #     ):
    #         return False
    #     return True

    # 8. Business methods
