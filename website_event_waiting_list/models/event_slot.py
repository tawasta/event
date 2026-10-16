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
from datetime import datetime

from odoo import models


class EventSlot(models.Model):
    _inherit = "event.slot"

    def _filter_open_slots(self):
        """Offer the full slots too when the event has a waiting list.

        Core lists only the slots that still have seats, so a visitor could
        never join the waiting list of a full slot.
        """
        open_slots = super()._filter_open_slots()
        waiting_slots = self.filtered(
            lambda slot: slot.event_id.waiting_list
            and slot.start_datetime > datetime.now()
        )
        return (open_slots | waiting_slots).sorted()
