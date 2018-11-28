# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):

    # 1. Private attributes
    _inherit = 'event.registration'

    # 2. Fields declaration
    consent_filled = fields.Boolean(
        string='Consent form filled',
        default=False,
        help='Has the user filled the consent form',
    )
    token = fields.Char(
        string='Random string to identify attendee',
        help='This field is used to identify attendee for ticket downloading',
        compute='_compute_uuid4',
        store=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    def _compute_uuid4(self):
        for record in self:
            record.token = uuid4()

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
