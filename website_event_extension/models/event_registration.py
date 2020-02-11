# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):

    # 1. Private attributes
    _inherit = 'event.registration'

    # 2. Fields declaration
    new_origin = fields.Char(
        string=_('Source'),
        compute='compute_new_origin'
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def compute_new_origin(self):
        sale_order = []

        for record in self:
            sale_order = self.env['sale.order'].search(
                [('name', '=', record.origin)])
            if sale_order:
                record.new_origin = sale_order.section_id.name or _("Internal")
            else:
                record.new_origin = _("Free ticket")
    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
