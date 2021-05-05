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
from odoo import fields, models, _
from odoo.http import request
from odoo.exceptions import ValidationError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WaitingMailListWizard(models.TransientModel):

    # 1. Private attributes
    _name = "event.waiting.mail.list.wizard"
    _description = "Create mailing list for waiting list contacts"

    # 2. Fields declaration
    registration_ids = fields.Many2many(
        "event.registration",
        default=lambda self: self.env['event.registration'].browse(self._context.get("active_ids")),
        string="Registrations",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def send_confirmation_mail(self):
        registration_ids = self.registration_ids
        cur_app = request.env["event.registration"]
        for registration in registration_ids:
            if registration.state != 'wait':
                raise ValidationError(_('All selected registrations must be in the waiting list.'))
            msg_template = request.env.ref(
                "event_waiting_list.event_waiting_registration"
            )
            values = {
                "email_to": registration.email,
                "email_from": registration.event_id.organizer_id.email_formatted,
                "subject": "We have available tickets for " + str(registration.event_id.name),
            }
            context = {
                'name': registration.name,
                'event': registration.event_id.name,
                'confirm_url': registration.confirm_url,
            }
            msg_template.sudo().write(values)
            msg_template.with_context(context).sudo().send_mail(
                cur_app.id, force_send=True
            )

    # 8. Business methods
