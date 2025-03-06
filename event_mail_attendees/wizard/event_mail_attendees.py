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
from odoo import _, api, fields, models
from odoo.exceptions import UserError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventMailAttendeesWizard(models.TransientModel):
    # 1. Private attributes
    _name = "event.mail.attendees.wizard"
    _description = "Event Mail Attendees Wizard"

    # 2. Fields declaration
    subject = fields.Char(
        "Subject", compute="_compute_subject", readonly=False, store=True, required=True
    )
    body = fields.Html(
        "Contents",
        sanitize_style=True,
        compute="_compute_body",
        readonly=False,
        store=True,
        required=True,
    )
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    template_id = fields.Many2one(
        "mail.template",
        "Use template",
        domain="[('model', '=', 'event.registration')]",
        readonly=True,
    )
    event_id = fields.Many2one("event.event", string="Event", required=True)
    recipients = fields.Many2many(
        "event.registration", string="Registrations", compute="_compute_attendees"
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("template_id")
    def _compute_subject(self):
        for msg in self:
            if msg.template_id:
                msg.subject = msg.template_id.subject
            else:
                msg.subject = False

    @api.depends("template_id")
    def _compute_body(self):
        for msg in self:
            if msg.template_id:
                msg.body = msg.template_id.body_html
            else:
                msg.body = False

    @api.depends("template_id", "event_id")
    def _compute_attendees(self):
        for msg in self:
            if msg.template_id:
                msg.recipients = msg.event_id.registration_ids.search(
                    [
                        "&",
                        ("event_id.id", "=", msg.event_id.id),
                        "|",
                        ("state", "=", "open"),
                        ("state", "=", "done"),
                    ]
                )
            else:
                msg.recipients = False

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def action_message(self):
        self.ensure_one()

        if not self.env.user.email:
            raise UserError(
                _(
                    "Unable to post message, please configure the sender's email address."
                )
            )

        mail_values = []
        for recipient in self.recipients:
            msg_template = self.template_id
            email_from_value = self.env["ir.config_parameter"].get_param(
                "event_sender_address"
            )
            mail_values = {
                "email_from": email_from_value or self.env.user.email_formatted,
                "subject": self.subject,
                "body_html": self.body,
                "email_to": recipient.email,
                "attachment_ids": self.attachment_ids.ids,
            }
            msg_template.sudo().send_mail(
                recipient.id, email_values=mail_values, force_send=True
            )
            recipient.sudo().message_post(
                subject=self.subject,
                body=self.body,
                attachment_ids=self.attachment_ids.ids,
            )

        self.event_id.sudo().message_post(
            subject=self.subject,
            body=self.body,
            attachment_ids=self.attachment_ids.ids,
            subtype_id=self.env.ref("event_mail_attendees.mt_mail_event_attendees").id,
        )

    # 8. Business methods
