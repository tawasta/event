##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        registrations = super(EventRegistration, self).create(vals_list)
        for registration in registrations:
            if (
                registration.event_ticket_id.product_id.batch_id
                and registration.attendee_partner_id
            ):
                vals = {
                    "partner_id": registration.attendee_partner_id.id,
                    "first_name": registration.attendee_partner_id.firstname,
                    "last_name": registration.attendee_partner_id.lastname,
                    "email": registration.attendee_partner_id.email,
                    "mobile": registration.attendee_partner_id.phone,
                }
                student_batch_vals = self.student_batch_values_preprocess(registration)
                is_student = (
                    self.env["op.student"]
                    .sudo()
                    .search([("partner_id", "=", registration.attendee_partner_id.id)])
                )
                if is_student:
                    current_student = is_student
                    student_batch_vals.update({"student_id": is_student.id})
                else:
                    create_student = self.env["op.student"].sudo().create(vals)
                    student_batch_vals.update({"student_id": create_student.id})
                    current_student = create_student

                already_found_in_batch = (
                    self.env["op.batch.students"]
                    .sudo()
                    .search(
                        [
                            ("student_id", "=", current_student.id),
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
        return registrations

    def unlink(self):
        self._unlink_associated_student_batch()
        return super(EventRegistration, self).unlink()

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

    def action_confirm(self):
        res = super(EventRegistration, self).action_confirm()
        if self.student_batch_id and self.event_id.create_partner_student_user:
            self.student_batch_id.student_id.create_student_user()
        return res

    # 8. Business methods
    def student_batch_values_preprocess(self, registration):
        values = {
            "batch_id": registration.event_ticket_id.product_id.batch_id.id,
            "event_id": registration.event_id.id,
            "event_registration_id": registration.id,
        }

        return values
