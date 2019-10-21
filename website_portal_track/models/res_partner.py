# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ResPartner(models.Model):
    # 1. Private attributes
    _inherit = 'res.partner'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields
    @api.multi
    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        res = super(ResPartner, self)._get_signup_url_for_action(
            action=action,
            view_type=view_type,
            menu_id=menu_id,
            res_id=res_id,
            model=model,
        )

        for partner in self:
            if partner.id in res and res[partner.id]:
                res[partner.id] += "&redirect=/my/tracks"

        return res

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
