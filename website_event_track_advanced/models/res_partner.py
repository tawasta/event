# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    returning_speaker = fields.Boolean(
        string='Has been a speaker at an earlier event',
        default=False,
    )

    # TODO: move this to reviewer
    review_group_ids = fields.Many2many(
        comodel_name='event.track.review.group',
        string='Review groups',
    )

    # TODO: move this to reviewer
    ratings_todo_count = fields.Integer(
        string='Ratings to do',
        compute='compute_ratings_todo',
    )

    # TODO: move this to reviewer
    ratings_done_count = fields.Integer(
        string='Ratings done',
        compute='compute_ratings_done',
    )

    # TODO: move this to reviewer
    ratings_done_percent = fields.Float(
        string='Rated %',
        compute='compute_ratings_percent',
    )

    def compute_ratings_todo(self):
        track = self.env['event.track']

        for record in self:
            record.ratings_todo_count = track.search_count([('message_partner_ids', '=', record.id)])

    def compute_ratings_done(self):
        rating = self.env['event.track.rating']
        users = self.env['res.users']

        for record in self:
            user = users.search([('partner_id', '=', record.id)])

            if user:
                record.ratings_done_count = rating.search_count([('create_uid', '=', user.id)])

    def compute_ratings_percent(self):
        for record in self:
            if record.ratings_todo_count:
                record.ratings_done_percent = float(record.ratings_done_count) / float(record.ratings_todo_count) * 100
