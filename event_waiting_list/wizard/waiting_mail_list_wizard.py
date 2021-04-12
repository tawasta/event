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
from odoo.exceptions import UserError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WaitingMailListWizard(models.TransientModel):

    # 1. Private attributes
    _name = "event.waiting.mail.list.wizard"
    _description = "Create mailing list for waiting list contacts"

    # 2. Fields declaration
    mail_list_id = fields.Many2one(
        comodel_name="mail.mass_mailing_list", string="Waiting Mailing List"
    )
    registration_ids = fields.Many2many(
        comodel_name="event.registrations",
        relation="mail_list_wizard_batch",
        default=lambda self: self.env.context.get("active_ids"),
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def add_to_waiting_mail_list(self):
        contact_obj = self.env["mail.mass_mailing.contact"]
        registrations = self.registration_ids
        waiting_registrations = registrations.mapped('state')
        partners = waiting_registrations.mapped('partner_id')
        user_data = []
        mail_list_contacts = self.mail_list_id.contact_ids.mapped("partner_id")

        for partner in partners:
            if partner.id not in mail_list_contacts.ids:
                if partner.email not in user_data:
                    if not partner.email:
                        raise UserError(
                            _("Partner '%s' has no email.") % partner.name
                        )
                    contact_vals = {
                        "partner_id": partner.id,
                        "list_ids": [[6, 0, [self.mail_list_id.id]]],
                        "title_id": partner.title or False,
                        "company_name": partner.company_id.name or False,
                        "country_id": partner.country_id or False,
                        "tag_ids": partner.category_id or False,
                    }
                    contact_obj.create(contact_vals)
                    user_data.append(partner.email)

    # 8. Business methods
