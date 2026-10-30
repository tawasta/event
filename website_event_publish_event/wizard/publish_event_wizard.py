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


class PublishEventWizard(models.TransientModel):
    _name = "website.event.publish.event.wizard"
    _description = "Action to publish all selected events on Website."

    event_ids = fields.Many2many(
        "event.event",
        default=lambda self: self.env["event.event"].browse(
            self.env.context.get("active_ids")
        ),
        string="Events",
    )

    def publish_event_on_website(self):
        self.event_ids.action_publish_event()
