# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventTrackProgramPath(models.Model):

    _name = 'event.track.program.path'

    name = fields.Char(
        string='Name',
        compute='compute_name',
        store=True,
    )

    url = fields.Char(
        string='Url',
        compute='compute_url',
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Owner',
        required=True,
    )

    track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Presentations',
    )

    @api.depends('user_id')
    def compute_name(self):
        for record in self:
            record.name = record.user_id.name

    @api.depends('track_ids')
    def compute_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url = base_url.rstrip('/')

        for record in self:
            if not record.track_ids:
                continue

            event = record.track_ids[0].event_id
            url = '%(url)s/event/%(event)s/program-path/%(program)s' % \
                  {
                     'url': base_url,
                     'event': event.id,
                     'program': record.id
                  }

            record.url = url
