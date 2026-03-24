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

import pytz
import werkzeug.urls

from odoo import api, fields, models

_logger = logging.getLogger(__name__)
GOOGLE_CALENDAR_URL = "https://www.google.com/calendar/render?"

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

    def _get_ics_file(self):
        """Returns iCalendar file for the event invitation.
        :returns a dict of .ics file content for each event
        """
        result = {}
        if not vobject:
            return result

        for event in self:
            cal = vobject.iCalendar()
            cal_event = cal.add("vevent")

            cal_event.add("created").value = fields.Datetime.now().replace(
                tzinfo=pytz.timezone("UTC")
            )
            cal_event.add("dtstart").value = fields.Datetime.from_string(
                event.date_begin
            ).replace(tzinfo=pytz.timezone("UTC"))
            cal_event.add("dtend").value = fields.Datetime.from_string(
                event.date_end
            ).replace(tzinfo=pytz.timezone("UTC"))
            cal_event.add("summary").value = event.name
            if event.address_id and not event.is_online_event:
                cal_event.add(
                    "location"
                ).value = event.sudo().address_id.contact_address
            elif event.is_online_event:
                cal_event.add("location").value = "Online"
            if event.video_conference_link:
                video_link = self.env_(
                    f"Join the video conference: {event.sudo().video_conference_link}"
                )
                cal_event.add("description").value = video_link

            result[event.id] = cal.serialize().encode("utf-8")
        return result

    def _get_event_resource_urls(self):
        url_date_start = self.date_begin.strftime("%Y%m%dT%H%M%SZ")
        url_date_stop = self.date_end.strftime("%Y%m%dT%H%M%SZ")
        params = {
            "action": "TEMPLATE",
            "text": self.name,
            "dates": url_date_start + "/" + url_date_stop,
            "details": self.name,
        }
        if self.address_id and not self.is_online_event:
            params.update(
                location=self.sudo().address_id.contact_address.replace("\n", " ")
            )
        elif self.is_online_event:
            params.update(location=self.env._("Online"))
        if self.video_conference_link:
            params.update(
                details=self.env._("Join the video conference: ")
                + self.sudo().video_conference_link
            )
        encoded_params = werkzeug.urls.url_encode(params)
        google_url = GOOGLE_CALENDAR_URL + encoded_params
        iCal_url = f"/event/{self.di}d/ics?{encoded_params}"
        return {"google_url": google_url, "iCal_url": iCal_url}
