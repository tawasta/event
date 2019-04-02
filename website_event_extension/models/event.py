# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import api, fields, models, _

# 4. Imports from Odoo modules:
from openerp.exceptions import Warning

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class Event(models.Model):

    # 1. Private attributes
    _inherit = 'event.event'

    # 2. Fields declaration
    # confirmable = fields.Boolean(string='Is event confirmable?', compute='compute_confirmable')

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.one
    def button_confirm(self):

        msg = _("Minium seats aren't filled!")

        # If minium seats are filled, you can confirm event
        if self.seats_reserved >= self.seats_min:

            super(Event, self).button_confirm()
        else:
            raise Warning(msg)

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
