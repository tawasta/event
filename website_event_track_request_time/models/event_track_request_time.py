# -*- coding: utf-8 -*-

# 1. Standard library imports:
import dateutil.parser

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackRequestTime(models.Model):
    # 1. Private attributes
    _name = 'event.track.request.time'
    _order = 'sequence'

    # 2. Fields declaration
    name = fields.Char(
        translate=True,
    )
    active = fields.Boolean(
        default=True,
    )
    start_time = fields.Datetime(
        string='Start time',
    )
    end_time = fields.Datetime(
        string='End time',
    )
    event_tracks = fields.One2many(
        comodel_name='event.track',
        inverse_name='request_time',
        string='Event track',
    )
    sequence = fields.Integer(
        string='Order',
    )

    # 3. Default methods

    # 4. Compute and search fields

    # 5. Constraints and onchanges
    @api.onchange('start_time', 'end_time')
    def onchange_time_compute_name(self):
        for record in self:
            start_time = ''
            end_time = ''

            if record.start_time:
                start_time = str(dateutil.parser.parse(record.start_time).time())[:5]

            if record.end_time:
                end_time = str(dateutil.parser.parse(record.end_time).time())[:5]

            record.name = "(%s - %s)" % (start_time, end_time)

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
