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
    _inherit = 'event.registration'

    # 2. Fields declaration
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('cancel', 'Cancelled'),
        ('wait', 'Waiting'),
        ('open', 'Confirmed'),
        ('done', 'Attended')],
                             string='Status', default='draft',
                             readonly=True, copy=False, tracking=True)

    product_url = fields.Char("Public link", compute="_compute_product_url")

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_product_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for registration in self:
            registration.product_url = urls.url_join(
                base_url, "/web/login?redirect=/shop/payment/update/%s" % (registration.id)
            )

    # 5. Constraints and onchanges
    @api.constrains('event_id', 'state')
    def _check_seats_limit(self):
        for registration in self:
            if (registration.event_id.seats_limited and registration.event_id.seats_max and registration.event_id.seats_available < (1 if registration.state == 'draft' else 0)) and not registration.event_id.waiting_list:
                raise ValidationError(_('No more seats available for this event.'))

    @api.constrains('event_ticket_id', 'state')
    def _check_ticket_seats_limit(self):
        for record in self:
            if (record.event_ticket_id.seats_max and record.event_ticket_id.seats_available < 0) and not record.event_ticket_id.waiting_list:
                raise ValidationError(_('No more available seats for this ticket'))

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        self = self.with_context(skip_confirm=True)
        registrations = super(EventRegistration, self).create(vals_list)

        if registrations._check_auto_confirmation_create():
            if registrations._check_waiting_list():
                registrations.sudo().action_waiting()
            else:
                registrations.sudo().action_confirm()
        elif registrations._check_waiting_list():
            registrations.sudo().action_waiting()

        return registrations

    def write(self, vals):
        ret = super(EventRegistration, self).write(vals)
        if vals.get('state') == 'open':
            # auto-trigger after_sub (on subscribe) mail schedulers, if needed
            onsubscribe_schedulers = self.mapped('event_id.event_mail_ids').filtered(lambda s: s.interval_type == 'after_sub')
            onsubscribe_schedulers.sudo().execute()
        if vals.get('state') == 'wait':
            # auto-trigger after_wait (on subscribe to waiting list) mail schedulers, if needed
            onsubscribe_schedulers = self.mapped('event_id.event_mail_ids').filtered(lambda s: s.interval_type == 'after_wait')
            onsubscribe_schedulers.sudo().execute()

        return ret

    # 7. Action methods
    def action_waiting(self):
        self.write({'state': 'wait'})

    def action_confirm(self):
        self.write({'state': 'open'})

    def _check_waiting_list(self):
        if any(not registration.event_id.waiting_list or
               (registration.event_id.seats_available) for registration in self):
            return False
        return True

    def _check_auto_confirmation(self):
        res = super()._check_auto_confirmation()
        # set res false when called from super to avoid confirm
        if self._context.get("skip_confirm"):
            res = False

        return res

    def _check_auto_confirmation_create(self):
        if any(not registration.event_id.auto_confirm or
               (not registration.event_id.seats_available and registration.event_id.seats_limited) for registration in self):
            return False
        return True

    # 8. Business methods
