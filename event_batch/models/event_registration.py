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
                    "first_name": "Etunimi",
                    "last_name": "Sukunimi",
                    "email": registration.partner_id.email,
                    "mobile": registration.partner_id.phone,
                    "birth_date": "1995-01-01",
                }
                create_student = self.env["op.student"].sudo().create(vals)

                if create_student:
                    student_batch_vals = {
                        "student_id": create_student.id,
                        "batch_id": registration.event_id.batch_id.id,
                        "event_id": registration.event_id.id,
                    }
                    create_student_batch = (
                        self.env["op.batch.students"].sudo().create(student_batch_vals)
                    )
        return registrations
