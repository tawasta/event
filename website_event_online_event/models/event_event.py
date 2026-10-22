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

import logging
import urllib.parse

import werkzeug.urls
from markupsafe import escape

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    import vobject
except ImportError:
    _logger.warning(
        "`vobject` Python module not found, iCal file generation disabled. "
        "Consider installing this module if you want to generate iCal files"
    )
    vobject = None


class EventType(models.Model):
    _inherit = "event.type"

    is_online_event = fields.Boolean(
        "Online Only Event",
        help="Online only events like webinars do not have a physical location and "
        "are hosted online.",
    )


class EventEvent(models.Model):
    _inherit = "event.event"

    is_online_event = fields.Boolean(
        "Online Only Event",
        help="Online only events like webinars do not have a physical location and "
        "are hosted online.",
        readonly=False,
        store=True,
        compute="_compute_is_online_event",
    )
    video_conference_link = fields.Char(readonly=False, store=True)

    @api.depends("event_type_id")
    def _compute_is_online_event(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            event.is_online_event = event.event_type_id.is_online_event

    def _get_external_description(self):
        """Add the video conference link to the description that core uses in
        the calendar file and in the calendar links."""
        description = super()._get_external_description()
        if self.video_conference_link:
            description += "\n" + self.env._(
                "Join the video conference: %s", escape(self.video_conference_link)
            )
        return description

    def _get_ics_file(self, slot=False):
        """Set the location of an online event to Online in the core file."""
        result = super()._get_ics_file(slot=slot)
        if not vobject:
            return result
        for event in self.filtered("is_online_event"):
            calendar = vobject.readOne(result[event.id].decode("utf-8"))
            if hasattr(calendar.vevent, "location"):
                calendar.vevent.location.value = "Online"
            else:
                calendar.vevent.add("location").value = "Online"
            result[event.id] = calendar.serialize().encode("utf-8")
        return result

    def _get_event_resource_urls(self, slot=False):
        """Set the location of an online event to Online in the Google link."""
        urls = super()._get_event_resource_urls(slot=slot)
        if self.is_online_event:
            google_url = urllib.parse.urlsplit(urls["google_url"])
            params = dict(urllib.parse.parse_qsl(google_url.query))
            params["location"] = self.env._("Online")
            urls["google_url"] = google_url._replace(
                query=werkzeug.urls.url_encode(params)
            ).geturl()
        return urls
