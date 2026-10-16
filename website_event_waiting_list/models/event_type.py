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


class EventType(models.Model):
    _inherit = "event.type"

    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        help="Enable waiting list when attendee limit is reached.",
        default=True,
    )

    def _default_event_mail_type_ids_with_waiting_list(self):
        """Extend core's own event-type mail-schedule defaults.

        Core stores a direct reference to its default method (not a name
        string), so overriding it would never run - the field is
        redeclared below with a new default calling this method through
        ``self`` instead. Wrapped in ``lambda self: ...`` there for the
        same reason, so a further module can still override this one too.
        """
        templates = self.env["event.mail"]._get_waiting_list_templates()
        return self._default_event_mail_type_ids() + [
            (
                0,
                0,
                {
                    "interval_nbr": 0,
                    "interval_unit": "now",
                    "interval_type": interval_type,
                    "template_ref": f"mail.template,{template.id}",
                },
            )
            for interval_type, template in templates.items()
        ]

    event_type_mail_ids = fields.One2many(
        "event.type.mail",
        "event_type_id",
        string="Mail Schedule",
        default=lambda self: self._default_event_mail_type_ids_with_waiting_list(),
    )
