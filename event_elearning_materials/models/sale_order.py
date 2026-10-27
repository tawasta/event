from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """
        Enroll attendees to the related course. Free registrations are
        confirmed already in the cart, so core's confirmation hook does not
        include them.
        """
        res = super().action_confirm()
        # sudo: salespersons without event rights may confirm event orders
        self.sudo().order_line.registration_ids._enroll_attendees_in_course()
        return res

    def _action_cancel(self):
        """
        Remove attendees from the related course. Cancelling the order
        recomputes the registration state without calling write().
        """
        # Only registrations that granted course access: cancelling a quotation
        # must not remove access the attendee got some other way
        # sudo: salespersons without event rights may cancel event orders
        registrations = (
            self.sudo().order_line.registration_ids._filter_granting_course_access()
        )
        res = super()._action_cancel()
        registrations.filtered(
            lambda reg: reg.state == "cancel"
        )._remove_attendee_from_course()
        return res
