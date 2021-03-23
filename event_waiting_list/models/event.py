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

# 3. Odoo imports (openerp):
from odoo import fields, models, api

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class Event(models.Model):

    # 1. Private attributes
    _inherit = 'event.event'

    # 2. Fields declaration
    waiting_list = fields.Boolean(
        string="Enable waiting list",
        help="Enable waiting list when attendee limit is reached.",
        default=True,
    )
    seats_waiting = fields.Integer(
        string="Seats on waiting list",
        store=True, readonly=True, compute='_compute_seats'
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.multi
    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        """ Determine waiting seats. """
        res = super(Event, self)._compute_seats()
        # init field to 0
        for event in self:
            event.seats_waiting = 0
        # add wait to state field
        state_field = {
            'wait': 'seats_waiting',
        }
        # add wait to sql query
        query = """ SELECT event_id, state, count(event_id)
                FROM event_registration
                WHERE event_id IN %s AND state IN ('draft', 'open', 'done', 'wait')
                GROUP BY event_id, state
                """
        # update res fields
        res['state_field'] += state_field
        res['query'] = query
        return res

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods


class EventRegistration(models.Model):

    # 1. Private attributes
    _inherit = 'event.registration'

    # 2. Fields declaration
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('cancel', 'Cancelled'),
        ('wait', 'Waiting'),
        ('open', 'Confirmed'),
        ('done', 'Attended')],
        string='Status', default='draft', readonly=True, copy=False, track_visibility='onchange')

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.one
    @api.constrains('event_id', 'state')
    def _check_seats_limit(self):
        if self.event_id.seats_availability == 'limited' and self.event_id.seats_max and self.event_id.seats_available < (1 if self.state == 'draft' else 0):
            pass

    # 6. CRUD methods

    # 7. Action methods
    @api.multi
    def _check_auto_confirmation(self):
        if self._context.get('registration_force_draft'):
            return False
        if any(registration.event_id.state != 'confirm'
               or not registration.event_id.auto_confirm
               for registration in self):
            return False
        return True

    @api.one
    def confirm_registration(self):
        if any((not registration.event_id.seats_available and registration.event_id.seats_availability == 'limited') for registration in self):
            self.state = 'wait'
        else:
            self.state = 'open'

        # auto-trigger after_sub (on subscribe) mail schedulers, if needed
        onsubscribe_schedulers = self.event_id.event_mail_ids.filtered(
            lambda s: s.interval_type == 'after_sub')
        onsubscribe_schedulers.execute()

    # 8. Business methods
