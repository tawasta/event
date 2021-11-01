from odoo import api, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model_create_multi
    def create(self, vals_list):
        print(vals_list)
        for values in vals_list:
            Partner = self.env["res.partner"]
            is_partner = Partner.search([("email", "=ilike", values.get("email"))], limit=1)
            print(is_partner)
            if not is_partner:
                partner_vals = {
                    'name': values.get("name"),
                    'email': values.get("email"),
                    'phone': values.get("phone"),
                }
                new_partner = Partner.sudo().create(partner_vals)
                values["partner_id"] = new_partner.id
            else:
                values["partner_id"] = is_partner.id

        registrations = super(EventRegistration, self).create(vals_list)
        for registration in registrations:
            if registration.event_ticket_id.product_id.batch_id:
                vals = {
                    "partner_id": registration.partner_id.id,
                    "first_name": registration.partner_id.firstname,
                    "last_name": registration.partner_id.lastname,
                    "email": registration.partner_id.email,
                    "mobile": registration.partner_id.phone,
                    "birth_date": "1995-01-01",
                }
                student_batch_vals = self.student_batch_values_preprocess(registration)

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

    def student_batch_values_preprocess(self, registration):
        values = {
            "batch_id": registration.event_ticket_id.product_id.batch_id.id,
            "event_id": registration.event_id.id,
        }

        return values
