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
from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WaitingMailListWizard(models.TransientModel):

    # 1. Private attributes
    _name = "website.event.waiting.mail.list.wizard"
    _description = "Create mailing list for waiting list contacts"

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
        registration_ids = self.registration_ids
        for registration in registration_ids:
            if not registration.waiting_list_to_confirm:
                raise ValidationError(
                    _(
                        "All selected registrations must be in the waiting list "
                        "and the Event/Ticket needs to have available seats."
                    )
                )
            msg_template = request.env.ref(
                "event_waiting_list.event_confirm_waiting_registration"
            )
            msg_template.send_mail(registration.id)

    # 8. Business methods
