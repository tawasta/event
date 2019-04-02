# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError


class TrackMailListWizard(models.TransientModel):
    _name = 'track.mail.list.wizard'
    _description = 'Create contact mailing list'

    mail_list_id = fields.Many2one(
        comodel_name='mail.mass_mailing.list',
        string='Mailing List'
    )
    track_ids = fields.Many2many(
        comodel_name='event.track',
        relation='mail_list_wizard_track',
        default=lambda self: self.env.context.get('active_ids'))

    @api.multi
    def add_to_mail_list(self):
        contact_obj = self.env['mail.mass_mailing.contact']
        for track in self.track_ids:

            contact = self._context.get('contact', False)

            if contact not in ['partner', 'speaker']:
                raise UserError(_("Invalid contact type"))

            if contact == 'partner':
                partners = track.partner_id
            if contact == 'speaker':
                partners = track.speaker_ids

            for partner in partners:
                if not partner.email:
                    raise UserError(_("Partner '%s' has no email.") % partner.name)
                criteria = [
                    '|',
                    ('email', '=', partner.email),
                    ('partner_id', '=', partner.id),
                    ('list_id', '=', self.mail_list_id.id),
                ]
                contact_test = contact_obj.search(criteria)
                if contact_test:
                    continue
                contact_vals = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'name': partner.name,
                    'list_id': self.mail_list_id.id
                }

                contact_obj.create(contact_vals)