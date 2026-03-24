from odoo import fields, models


class EventStage(models.Model):
    _inherit = "event.stage"

    pipe_publish = fields.Boolean(
        string="Published Stage",
        default=False,
        help="Published events are automatically moved into this stage. "
        "The event moved into this stage are published automatically.",
    )
