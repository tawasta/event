# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):

    # 1. Private attributes
    _inherit = 'event.registration'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    @api.one
    def confirm_registration(self):
        """
        Update partner from SO to registration
        """
        if self.sale_order_id:
            self.write({
                'partner_id': self.sale_order_id.partner_id.id,
            })
        super(EventRegistration, self).confirm_registration()

    # 8. Business methods
