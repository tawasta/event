# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrackType(models.Model):
    # 1. Private attributes
    _name = 'event.track.type'

    # 2. Fields declaration
    code = fields.Char(
        copy=False,
        translate=False,
    )

    name = fields.Char(translate=True)

    description = fields.Html(translate=True)

    active = fields.Boolean(
        default=True
    )

    event_tracks = fields.One2many(
        comodel_name='event.track',
        inverse_name='type',
        string='Event track',
    )

    show_in_proposals = fields.Boolean(
        string='Show in proposals',
        help='Show in proposals form',
        default=True,
    )

    show_in_agenda = fields.Boolean(
        string='Show in agenda',
        help='Show in website agenda',
        default=True,
    )

    attendable = fields.Boolean(
        string='Attendable',
        help='If the presentation type can be attended. Unattendable types will be muted in the agenda',
        default=True,
    )

    # 3. Default methods

    # 4. Compute and search fields

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
