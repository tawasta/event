from odoo import api, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model_create_multi
    def create(self, vals_list):
        registrations = super(EventRegistration, self).create(vals_list)
        for registration in registrations:
            if registration.event_id.batch_id:
                vals = {
                    "partner_id": registration.partner_id.id,
                    "first_name": registration.partner_id.firstname,
                    "last_name": registration.partner_id.lastname,
                    "email": registration.partner_id.email,
                    "mobile": registration.partner_id.phone,
                    "birth_date": "1995-01-01",
                }
                student_batch_vals = {
                    "batch_id": registration.event_id.batch_id.id,
                    "event_id": registration.event_id.id,
                }
                is_student = self.env["op.student"].sudo().search([
                    ('partner_id', '=', registration.partner_id.id)
                ])
                if is_student:
                    student_batch_vals.update({"student_id": is_student.id})
                else:
                    create_student = self.env["op.student"].sudo().create(vals)
                    student_batch_vals.update({"student_id": create_student.id})

                create_student_batch = (
                    self.env["op.batch.students"].sudo().create(student_batch_vals)
                )
        return registrations
