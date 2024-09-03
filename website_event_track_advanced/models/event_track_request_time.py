# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackRequestTime(models.Model):
    # 1. Private attributes
    _name = "event.track.request.time"
    _order = "sequence"

    # 2. Fields declaration
    name = fields.Char(
        translate=True,
    )
    active = fields.Boolean(
        default=True,
    )
    start_time = fields.Datetime(
        string="Start time",
    )
    end_time = fields.Datetime(
        string="End time",
    )
    event_tracks = fields.One2many(
        comodel_name="event.track",
        inverse_name="request_time",
        string="Event track",
    )
    sequence = fields.Integer(
        string="Order",
    )
