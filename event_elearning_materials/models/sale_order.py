from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_cancel(self):
        """
        Remove attendees from the related course. Cancelling the order
        recomputes the registration state without calling write().
        """
        # Only confirmed registrations granted course access: cancelling a
        # quotation must not remove access the attendee got some other way
        # sudo: salespersons without event rights may cancel event orders
        registrations = self.sudo().order_line.registration_ids.filtered(
            lambda reg: reg.state in ("open", "done")
        )
        res = super()._action_cancel()
        registrations.filtered(
            lambda reg: reg.state == "cancel"
        )._remove_attendee_from_course()
        return res
