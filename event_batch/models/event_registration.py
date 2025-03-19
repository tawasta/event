##############################################################################
#
#    Author: Futural Oy
#    Copyright 2022- Futural Oy (https://futural.fi)
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


import logging

# 3. Odoo imports (openerp):
from odoo import api, fields, models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)
# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
    student_batch_id = fields.Many2one(
        "op.batch.students",
        string="Student Batch",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    # Kenttien uudelleenmäärittely, jotta uusi funktio varmasti rekisteröidään
    sale_status = fields.Selection(
        selection=[
            ("to_pay", "Not Sold"),
            ("sold", "Sold"),
            ("free", "Free"),
        ],
        compute="_compute_registration_status",  # Pakotetaan uusi funktio
        compute_sudo=True,
        store=True,
        precompute=True,
    )

    state = fields.Selection(
        default=None,
        compute="_compute_registration_status",  # Pakotetaan uusi funktio
        store=True,
        readonly=False,
        precompute=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    def create_student_batch(self):
        registration = self
        if registration.event_ticket_id.product_id.batch_id:
            student_batch_vals = self.student_batch_values_preprocess(registration)

            vals = {
                "partner_id": registration.attendee_partner_id.id,
                "first_name": registration.attendee_partner_id.firstname,
                "last_name": registration.attendee_partner_id.lastname,
                "email": registration.attendee_partner_id.email,
                "mobile": registration.attendee_partner_id.phone,
            }

            if not vals.get("first_name") and not vals.get("last_name"):
                # If attendee is not set
                vals["name"] = registration.name

            is_student = (
                self.env["op.student"]
                .sudo()
                .search(
                    [("partner_id", "=", registration.attendee_partner_id.id)],
                    limit=1,
                )
            )

            if is_student:
                student_batch_vals.update({"student_id": is_student.id})

                already_found_in_batch = (
                    self.env["op.batch.students"]
                    .sudo()
                    .search(
                        [
                            ("student_id", "=", is_student.id),
                            (
                                "batch_id",
                                "=",
                                registration.event_ticket_id.product_id.batch_id.id,
                            ),
                        ]
                    )
                )

                if not already_found_in_batch:
                    student_batch_vals.update({"first_time": True})

            if not is_student:
                create_student = self.env["op.student"].sudo().create(vals)

                student_batch_vals.update({"student_id": create_student.id})
                already_found_in_batch = (
                    self.env["op.batch.students"]
                    .sudo()
                    .search(
                        [
                            ("student_id", "=", create_student.id),
                            (
                                "batch_id",
                                "=",
                                registration.event_ticket_id.product_id.batch_id.id,
                            ),
                        ]
                    )
                )

                if not already_found_in_batch:
                    student_batch_vals.update({"first_time": True})

            student_batch = (
                self.env["op.batch.students"].sudo().create(student_batch_vals)
            )

            registration.student_batch_id = student_batch.id

    def unlink(self):
        self._unlink_associated_student_batch()
        return super(EventRegistration, self).unlink()

    def action_cancel(self):
        current_student_batch = False
        if self.student_batch_id:
            current_student_batch = self.student_batch_id
        res = super().action_cancel()
        if current_student_batch:
            current_student_batch.unlink()

        return res

    # 7. Action methods
    def _unlink_associated_student_batch(self):
        for registration in self:
            if (
                registration.student_batch_id
                and registration.student_batch_id.state == "draft"
            ):
                self.env["op.batch.students"].search(
                    [("event_registration_id", "=", registration.id)]
                ).unlink()

    def write(self, vals):
        if self.env.context.get("no_create_batch"):
            return super(EventRegistration, self).write(vals)
        res = super(EventRegistration, self).write(vals)
        for rec in self:
            if rec.state == "open":
                if not rec.student_batch_id:
                    _logger.info("===LUODAAN STUDENT BATCH=== for record: %s", rec)
                    rec.with_context(no_create_batch=True).create_student_batch()
        return res

    @api.depends(
        "sale_order_id.state",
        "sale_order_id.currency_id",
        "sale_order_line_id.price_total",
    )
    def _compute_registration_status(self):
        _logger.info("Compute function _compute_registration_status called")
        for so_line, registrations in self.grouped("sale_order_line_id").items():
            cancelled_so_registrations = registrations.filtered(
                lambda reg: reg.sale_order_id.state == "cancel"
            )
            cancelled_so_registrations.state = "cancel"
            cancelled_registrations = (
                cancelled_so_registrations
                | registrations.filtered(lambda reg: reg.state == "cancel")
            )
            if not so_line or float_is_zero(
                so_line.price_total, precision_rounding=so_line.currency_id.rounding
            ):
                registrations.sale_status = "free"
                registrations.filtered(
                    lambda reg: not reg.state or reg.state == "draft"
                ).state = "open"
                # Lisätty toiminnallisuus
                for rec in registrations:
                    if rec.state == "open" and not rec.student_batch_id:
                        _logger.info("===LUODAAN STUDENT BATCH=== for record: %s", rec)
                        rec.with_context(no_create_batch=True).create_student_batch()

            else:
                sold_registrations = (
                    registrations.filtered(
                        lambda reg: reg.sale_order_id.state == "sale"
                    )
                    - cancelled_registrations
                )
                sold_registrations.sale_status = "sold"
                (registrations - sold_registrations).sale_status = "to_pay"
                sold_registrations.filtered(
                    lambda reg: not reg.state or reg.state in {"draft", "cancel"}
                ).state = "open"
                # Lisätty toiminnallisuus
                for rec in sold_registrations:
                    if rec.state == "open" and not rec.student_batch_id:
                        _logger.info("===LUODAAN STUDENT BATCH=== for record: %s", rec)
                        rec.with_context(no_create_batch=True).create_student_batch()
                (
                    registrations - sold_registrations - cancelled_registrations
                ).state = "draft"

    # 8. Business methods
    def student_batch_values_preprocess(self, registration):
        values = {
            "batch_id": registration.event_ticket_id.product_id.batch_id.id,
            "event_id": registration.event_id.id,
            "event_registration_id": registration.id,
        }

        return values
