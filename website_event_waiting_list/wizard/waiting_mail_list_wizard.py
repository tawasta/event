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
from odoo import fields, models


class WaitingMailListWizard(models.TransientModel):
    _name = "website.event.waiting.mail.list.wizard"
    _description = "Mail confirmation email to waiting list contacts"

    registration_ids = fields.Many2many(
        "event.registration",
        default=lambda self: self._default_registration_ids(),
        string="Registrations",
    )

    def _default_registration_ids(self):
        context = self.env.context
        if context.get("active_model") != "event.registration":
            return self.env["event.registration"]
        return self.env["event.registration"].browse(context.get("active_ids"))

    def send_confirmation_mail(self):
        self.ensure_one()
        template = self.env.ref(
            "website_event_waiting_list.event_confirm_waiting_registration"
        )
        sent = self.registration_ids.filtered(
            lambda registration: registration.email
            and registration.waiting_list_to_confirm
        )
        for registration in sent:
            template.sudo().send_mail(registration.id, force_send=True)
        self._mark_notified(sent)
        message = self.env["website.event.waiting.mail.list.message"].create(
            {
                "message": self.env._(
                    "Waiting list confirmation mail sent to following registrations:"
                ),
                "registration_ids": sent.ids,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": message._name,
            "view_mode": "form",
            "res_id": message.id,
            "target": "new",
        }

    def _mark_notified(self, registrations):
        """Record the mails as sent, so the automatic "seats available" mail does
        not send the same mail again to the same registrations."""
        for event, event_registrations in registrations.grouped("event_id").items():
            event.sudo().event_mail_ids.filtered(
                lambda scheduler: scheduler.interval_type == "after_seats_available"
            )._mark_mail_sent(event_registrations)
