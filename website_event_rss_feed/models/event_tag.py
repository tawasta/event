from odoo import fields, models


class EventTag(models.Model):
    _inherit = "event.tag"

    event_multifeed_ids = fields.Many2many(
        "event.multifeed",
        string="Event multifeeds",
        help="Event RSS multifeeds this tag's events are shown in.",
    )
