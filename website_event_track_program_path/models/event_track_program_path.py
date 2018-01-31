# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventTrackProgramPath(models.Model):

    _name = 'event.track.program.path'

    name = fields.Char(
        string='Name',
        compute='compute_name',
        store=True,
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
