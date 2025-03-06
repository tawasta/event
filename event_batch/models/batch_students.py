# 1. Standard library imports:
# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class OpBatchStudents(models.Model):
    # 1. Private attributes
    _inherit = "op.batch.students"

    # 2. Fields declaration
    event_id = fields.Many2one(string="Event", comodel_name="event.event")
    event_registration_id = fields.Many2one(
        string="Event Registration", comodel_name="event.registration"
    )

    first_time = fields.Boolean(string="First time", default=False)

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
