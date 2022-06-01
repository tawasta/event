##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
from odoo.exceptions import UserError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class TrackMailListWizard(models.TransientModel):
    # 1. Private attributes
    _name = "track.mail.list.wizard"
    _description = "Create contact mailing list"

    # 2. Fields declaration
    mail_list_id = fields.Many2one(comodel_name="mailing.list", string="Mailing List")
    track_ids = fields.Many2many(
        comodel_name="event.track",
        relation="mail_list_wizard_track",
        default=lambda self: self.env.context.get("active_ids"),
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def add_to_mail_list(self):
        contact_obj = self.env["mailing.contact"]
        for track in self.track_ids:
            contact = self._context.get("contact", False)
            if contact not in ["partner", "speaker"]:
                raise UserError(_("Invalid contact type"))

            if contact == "partner":
                partners = track.partner_id
            if contact == "speaker":
                partners = track.speaker_ids

            for partner in partners:
                if not partner.email:
                    raise UserError(_("Partner '%s' has no email.") % partner.name)
                criteria = [
                    "|",
                    ("email", "=", partner.email),
                    ("partner_id", "=", partner.id),
                    ("list_ids", "=", self.mail_list_id.id),
                ]
                contact_test = contact_obj.search(criteria)
                if contact_test:
                    continue
                contact_vals = {
                    "partner_id": partner.id,
                    "list_ids": [(4, self.mail_list_id.id)],
                    "email": partner.email,
                    "name": partner.name,
                    "title_id": partner.title or False,
                    "company_name": partner.company_id.name or False,
                    "country_id": partner.country_id or False,
                    "tag_ids": partner.category_id or False,
                }

                contact_obj.create(contact_vals)

    # 8. Business methods
