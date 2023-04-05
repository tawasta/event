# 1. Standard library imports:
# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import fields, models
import logging

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class SaleOrderLine(models.Model):

    # 1. Private attributes
    _inherit = "sale.order.line"

    # 2. Fields declaration

    # 3. Default methods
    def _update_registrations(self, confirm=True, cancel_to_draft=False, registration_data=None, mark_as_paid=False):
        """ Create or update registrations linked to a sales order line. A sale
        order line has a product_uom_qty attribute that will be the number of
        registrations linked to this line. This method update existing registrations
        and create new one for missing one. """
        logging.info("====================UPDATE========================");
        RegistrationSudo = self.env['event.registration'].sudo()
        registrations = RegistrationSudo.search([('sale_order_line_id', 'in', self.ids)])
        registrations_vals = []
        for so_line in self.filtered('event_id'):
            existing_registrations = registrations.filtered(lambda self: self.sale_order_line_id.id == so_line.id)
            if confirm:
                logging.info("========CONFIRM=========");
                existing_registrations.filtered(lambda self: self.state not in ['open', 'cancel']).action_confirm()
            if mark_as_paid:
                logging.info("========MARK AS PAID=========");
                existing_registrations.filtered(lambda self: not self.is_paid)._action_set_paid()
            if cancel_to_draft:
                logging.info("========DRAFT=========");
                existing_registrations.filtered(lambda self: self.state == 'cancel').action_set_draft()

            for count in range(int(so_line.product_uom_qty) - len(existing_registrations)):
                values = {
                    'sale_order_line_id': so_line.id,
                    'sale_order_id': so_line.order_id.id
                }
                # TDE CHECK: auto confirmation
                if registration_data:
                    values.update(registration_data.pop())
                registrations_vals.append(values)

        if registrations_vals:
            logging.info("========REGISTRATION=========");
            RegistrationSudo.create(registrations_vals)
        return True

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
