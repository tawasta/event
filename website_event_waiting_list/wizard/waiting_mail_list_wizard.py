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
# 1. Standard library imports:
# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WaitingMailListWizard(models.TransientModel):
    # 1. Private attributes
    _name = "website.event.waiting.mail.list.wizard"
    _description = "Mail confirmation email to waiting list contacts"

    # 2. Fields declaration
    registration_ids = fields.Many2many(
        "event.registration",
        default=lambda self: self.env["event.registration"].browse(
            self._context.get("active_ids")
        ),
        string="Registrations",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def send_confirmation_mail(self):
        self.ensure_one()
        msg_template = self.env.ref(
            "website_event_waiting_list.event_confirm_waiting_registration"
        )
        registrations_sent = self.registration_ids.filtered(
            lambda registration: registration.email
            and registration.waiting_list_to_confirm
        )
        for registration in registrations_sent:
            msg_template.sudo().send_mail(registration.id, force_send=True)

        message = self.env["website.event.waiting.mail.list.message"].create(
            {
                "message": self.env._(
                    "Waiting list confirmation mail sent to following "
                    "registrations:"
                ),
                "registration_ids": registrations_sent.ids,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "website.event.waiting.mail.list.message",
            "view_mode": "form",
            "res_id": message.id,
            "target": "new",
        }

    # 8. Business methods
