from odoo import api, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.model
    def create(self, vals_list):
        """
        Override the create method to trigger the sale order line description update
        when `sale_order_line_id` is set during record creation.
        """
        registrations = super().create(vals_list)
        if "sale_order_line_id" in vals_list:
            for registration in registrations:
                if registration.sale_order_line_id:
                    registration.sale_order_line_id._compute_name()
        return registrations

    def write(self, vals):
        """
        Override the write method to trigger the sale order line description update
        when `sale_order_line_id` is updated.
        """
        result = super().write(vals)
        if "sale_order_line_id" in vals:
            for registration in self:
                if registration.sale_order_line_id:
                    registration.sale_order_line_id._compute_name()
        return result
