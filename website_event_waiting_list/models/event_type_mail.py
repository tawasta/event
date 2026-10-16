##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################
from odoo import fields, models

from .event_mail import (
    WAITING_LIST_INTERVAL_ONDELETE,
    WAITING_LIST_INTERVAL_SELECTION,
)


class EventTypeMail(models.Model):
    _inherit = "event.type.mail"

    interval_type = fields.Selection(
        selection_add=WAITING_LIST_INTERVAL_SELECTION,
        ondelete=WAITING_LIST_INTERVAL_ONDELETE,
    )
