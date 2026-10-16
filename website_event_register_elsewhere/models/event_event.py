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
from urllib.parse import urlparse

from odoo import api, fields, models
from odoo.exceptions import ValidationError

REGISTRATION_ELSEWHERE_HELP = (
    "Registration is made on another website: the Register button of the event "
    "opens the registration link, and the event cannot be registered to in Odoo."
)
REGISTRATION_LINK_HELP = (
    "Address of the website where the registration is made. It must start with "
    "http:// or https://"
)


def _check_registration_link(env, record):
    """The link goes to the visitors, so only web addresses are accepted."""
    url = urlparse(record.registration_link or "")
    if url.scheme not in ("http", "https") or not url.netloc:
        raise ValidationError(
            env._(
                "The registration link of %(name)s must be a web address that "
                "starts with http:// or https://",
                name=record.name,
            )
        )


class EventType(models.Model):
    _inherit = "event.type"

    registration_elsewhere = fields.Boolean(
        string="Register Elsewhere", help=REGISTRATION_ELSEWHERE_HELP
    )
    registration_link = fields.Char(
        string="Registration Link (URL)", help=REGISTRATION_LINK_HELP
    )

    @api.constrains("registration_elsewhere", "registration_link")
    def _check_registration_link(self):
        for event_type in self.filtered("registration_elsewhere"):
            _check_registration_link(self.env, event_type)


class EventEvent(models.Model):
    _inherit = "event.event"

    registration_elsewhere = fields.Boolean(
        string="Register Elsewhere",
        compute="_compute_registration_elsewhere",
        readonly=False,
        store=True,
        precompute=True,
        help=REGISTRATION_ELSEWHERE_HELP,
    )
    registration_link = fields.Char(
        string="Registration Link (URL)",
        compute="_compute_registration_link",
        readonly=False,
        store=True,
        precompute=True,
        help=REGISTRATION_LINK_HELP,
    )

    @api.depends("event_type_id")
    def _compute_registration_elsewhere(self):
        """Copy the setting from the template when it changes, not when it is edited."""
        for event in self:
            event.registration_elsewhere = (
                event.event_type_id or event
            ).registration_elsewhere

    @api.depends("event_type_id")
    def _compute_registration_link(self):
        for event in self:
            event.registration_link = (event.event_type_id or event).registration_link

    @api.depends("registration_elsewhere", "kanban_state", "date_end")
    def _compute_event_registrations_open(self):
        """The seats and tickets of Odoo mean nothing when the registration is
        made elsewhere: the event is open until it is cancelled or over."""
        res = super()._compute_event_registrations_open()
        now = fields.Datetime.now()
        for event in self.filtered("registration_elsewhere"):
            event.event_registrations_open = event.kanban_state != "cancel" and (
                not event.date_end or event.date_end >= now
            )
        return res

    @api.constrains("registration_elsewhere", "registration_link")
    def _check_registration_link(self):
        for event in self.filtered("registration_elsewhere"):
            _check_registration_link(self.env, event)
