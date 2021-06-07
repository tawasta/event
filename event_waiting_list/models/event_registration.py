##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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

# 1. Standard library imports:

# 2. Known third party imports:
from werkzeug import urls

# 3. Odoo imports (openerp):
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):

    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
    waiting_list = fields.Boolean(related="event_id.waiting_list", store=True)
    waiting_list_to_confirm = fields.Boolean(
        string="Available to confirm from waiting list",
        readonly=True,
        compute_sudo=True,
        compute="_compute_available_to_confirm",
    )
    state = fields.Selection(selection_add=[("wait", "Waiting")])

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_available_to_confirm(self):
        """
        Compute all cases where registration from waiting list is able
        to be confirmed:
        1. Both ticket and event have limited but available seats
        2. Both ticket and event have no limited seats
        3. Ticket has no limited seats and event has limited but available seats
        4. Ticket has limited but available seats and event has no limited seats
        5. No ticket used and event has available seats
        """
        for registration in self:
            if (
                registration.waiting_list
                and registration.state == "wait"
                and (
                    (
                        not registration.event_id.seats_limited
                        or not registration.event_id.seats_max
                    )
                    or (
                        registration.event_id.seats_available > 0
                        and registration.event_id.seats_limited
                        and registration.event_id.seats_max
                    )
                )
                and (
                    (
                        not registration.event_ticket_id
                        or not registration.event_ticket_id.seats_limited
                        or not registration.event_ticket_id.seats_max
                    )
                    or (
                        registration.event_ticket_id.seats_available > 0
                        and registration.event_ticket_id.seats_limited
                        and registration.event_ticket_id.seats_max
                    )
                )
            ):
                registration.waiting_list_to_confirm = True
            else:
                registration.waiting_list_to_confirm = False

    def _compute_confirm_url(self):
        """ Url to confirm registration (move state from wait -> open) """
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for registration in self:
            registration.confirm_url = urls.url_join(
                base_url,
                "/event/%s/waiting-list/confirm/%s"
                % (registration.event_id.id, registration.access_token),
            )

    # 5. Constraints and onchanges
    @api.constrains("event_id", "state")
    def _check_seats_limit(self):
        """
        Raise validation error if no waiting list and seats are full
        Or if seats are full and trying to confirm a registration
        """
        for registration in self:
            for registration in self:
                if (
                    registration.event_id.seats_limited
                    and registration.event_id.seats_max
                    and registration.event_id.seats_available
                    < (1 if registration.state == "draft" else 0)
                ):
                    if not registration.event_id.waiting_list:
                        raise ValidationError(
                            _("No more seats available for this event.")
                        )
                    if (
                        registration.event_id.waiting_list
                        and registration.state not in ["draft", "wait"]
                    ):
                        raise ValidationError(
                            _("No more seats available for this event.")
                        )

    @api.constrains("event_ticket_id", "state")
    def _check_ticket_seats_limit(self):
        """
        Raise validation error if no waiting list and seats are full
        Or if seats are full and trying to confirm a registration
        """
        for registration in self:
            if (
                registration.event_ticket_id.seats_max
                and registration.event_ticket_id.seats_available < 0
            ):
                if not registration.event_ticket_id.waiting_list:
                    raise ValidationError(_("No more seats available for this ticket."))
                if (
                    registration.event_ticket_id.waiting_list
                    and registration.state not in ["draft", "wait"]
                ):
                    raise ValidationError(_("No more seats available for this ticket."))

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to assign correct state. Includes 3 cases.
        1. Auto confirm when available seats and auto confirm enabled
        2. Add to waiting list when no available seats and waiting list enabled
        3. Add registration as draft otherwise
        """
        # pass context to skip auto_confirm on super method
        self = self.with_context(skip_confirm_wait=True)
        registrations = super(EventRegistration, self).create(vals_list)
        registrations = registrations.with_context(skip_confirm_wait=False)
        for registration in registrations:
            if not registration.access_token:
                registration.sudo().write({"access_token": str(uuid.uuid4())})
        if registrations._check_auto_confirmation():
            registrations.sudo().action_confirm()
        elif registrations._check_waiting_list():
            registrations.sudo().action_waiting()
        return registrations

    def write(self, vals):
        """ Auto-trigger mail schedulers on state writes """
        ret = super(EventRegistration, self).write(vals)
        if vals.get("state") == "open":
            onsubscribe_schedulers = self.mapped("event_id.event_mail_ids").filtered(
                lambda s: s.interval_type == "after_sub"
            )
            onsubscribe_schedulers.sudo().execute()
        if vals.get("state") == "wait":
            onsubscribe_schedulers = self.mapped("event_id.event_mail_ids").filtered(
                lambda s: s.interval_type == "after_wait"
            )
            onsubscribe_schedulers.sudo().execute()
        return ret

    # 7. Action methods
    def action_waiting(self):
        if not self.event_id.waiting_list:
            raise ValidationError(_("Waiting list for this event is not enabled."))
        self.write({"state": "wait"})

    def _check_waiting_list(self):
        if any(
            not registration.event_id.waiting_list
            or (
                registration.event_id.seats_available >= 1
                and registration.event_ticket_id.seats_available >= 1
            )
            for registration in self
        ):
            return False
        return True

    def _check_auto_confirmation(self):
        if self._context.get("skip_confirm") or self._context.get("skip_confirm_wait"):
            return False
        if any(
            not registration.event_id.auto_confirm
            or (
                registration.event_id.seats_available <= 0
                and registration.event_id.seats_limited
                or registration.event_ticket_id.seats_available <= 0
                and registration.event_ticket_id.seats_limited
            )
            for registration in self
        ):
            return False
        return True

    # 8. Business methods
