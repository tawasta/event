from odoo import fields, models


class EventEvent(models.Model):

    _inherit = "event.event"

    is_promoted = fields.Boolean(
        "Promoted",
        help="The front-end Events snippet can be configured to show only promoted events.",
    )
