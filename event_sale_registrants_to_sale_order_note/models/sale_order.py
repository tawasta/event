from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """Adds linked registrations to a sale order's note field"""
        res = super(SaleOrder, self).action_confirm()
        for so in self:
            registrations = (
                self.env["event.registration"]
                .sudo()
                .search([("sale_order_id", "in", so.ids), ("state", "!=", "cancel")])
            )
            if registrations:
                registration_names = []
                for registration in registrations:
                    registration_names.append(registration.name)
                registrations_note = _("Linked Registrations: %s") % ",".join(
                    registration_names
                )
                if so.note:
                    new_note = so.note + "\n" + registrations_note
                else:
                    new_note = registrations_note
                so.sudo().write({"note": new_note})
        return res
