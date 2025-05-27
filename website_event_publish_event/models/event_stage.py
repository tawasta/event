from odoo import fields, models


class EventStage(models.Model):
    # 1. Private attributes
    _inherit = "event.stage"

    # 2. Fields declaration
    pipe_publish = fields.Boolean(
        string="Published Stage",
        default=False,
        help="Published events are automatically moved into this stage. "
        "The event moved into this stage are published automatically.",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
