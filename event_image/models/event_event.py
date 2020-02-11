# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):

    # 1. Private attributes
    _inherit = 'event.event'

    # 2. Fields declaration

    image = fields.Binary(
        string='Event image',
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
