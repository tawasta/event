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
import uuid

from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_join

from odoo import api, fields, models

CANCELLABLE_STATES = ("draft", "open")


class EventRegistration(models.Model):
    _inherit = "event.registration"

    access_token = fields.Char(
        "Security Token",
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: str(uuid.uuid4()),
    )
    manage_url = fields.Char("Public link", compute="_compute_manage_url")
    cancel_before_date = fields.Datetime(
        "Cancel registration before date",
        compute="_compute_cancel_before_date",
        help="Latest moment the attendee can cancel. Counted from the start of "
        "the selected slot, or from the start of the event if it has no slots.",
    )
    able_to_cancel = fields.Boolean(
        "Able to cancel registration", compute="_compute_able_to_cancel"
    )

    @api.depends("event_id", "access_token")
    def _compute_manage_url(self):
        """Public URL where the attendee can manage this registration."""
        for registration in self:
            registration.manage_url = url_join(
                registration.get_base_url(),
                f"/event/{registration.event_id.id}"
                f"/registration/manage/{registration.access_token}",
            )

    @api.depends(
        "event_slot_id.start_datetime",
        "event_id.date_begin",
        "event_id.cancel_interval_nbr",
        "event_id.cancel_interval_unit",
    )
    def _compute_cancel_before_date(self):
        for registration in self:
            event = registration.event_id
            start = registration.event_slot_id.start_datetime or event.date_begin
            if not start or not event.cancel_interval_unit:
                registration.cancel_before_date = False
                continue
            interval = relativedelta(
                **{event.cancel_interval_unit: event.cancel_interval_nbr}
            )
            registration.cancel_before_date = start - interval

    @api.depends("state", "cancel_before_date", "event_id.has_cancel")
    def _compute_able_to_cancel(self):
        # Not stored: the result depends on the current time
        now = fields.Datetime.now()
        for registration in self:
            registration.able_to_cancel = bool(
                registration.event_id.has_cancel
                and registration.state in CANCELLABLE_STATES
                and registration.cancel_before_date
                and now <= registration.cancel_before_date
            )
