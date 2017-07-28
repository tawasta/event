# -*- coding: utf-8 -*-

# 1. Standard library imports:
import difflib

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models
from odoo import _
from odoo.tools import html2plaintext
from odoo.exceptions import AccessError

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrack(models.Model):
    # 1. Private attributes
    _inherit = 'event.track'

    # 2. Fields declaration
    partner_id = fields.Many2one(
        string='Contact',
    )

    attachment_ids = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name='res_id',
        domain=[('res_model', '=', 'event.track')],
        string='Attachments',
    )

    description_original = fields.Html(
        string='Original description',
        readonly=True,
    )

    ratings = fields.One2many(
        comodel_name='event.track.rating',
        inverse_name='event_track',
        string='Ratings',
    )

    rating = fields.Selection(
        [
            ('0', 'Not rated'),
            ('1', 'Weak'),
            ('2', 'Decent'),
            ('3', 'Good'),
            ('4', 'Great'),
            ('5', 'Excellent'),
        ],
        select=True,
        string='Rating',
        compute='_get_rating',
        inverse='_set_rating',
    )

    type = fields.Many2one(
        comodel_name='event.track.type',
        inverse_name='event_track',
        string='Type',
    )

    rating_avg = fields.Float(
        digits=(3, 2),
        string='Rating',
        compute='_compute_rating_avg',
    )

    target_group = fields.Many2one(
        comodel_name='event.track.target.group',
        relation='event_track',
        string='Target group',
    )

    target_group_info = fields.Text(
        string='Target group info',
    )

    video_url = fields.Char(
        string='Track as a video (link to e.g. Youtube or Vimeo)'
    )

    review_group = fields.Many2one(
        comodel_name='event.track.review.group',
        string='Review group',
    )

    webinar = fields.Boolean(
        string='Pre-event webinar'
    )
    webinar_info = fields.Text(
        string='Pre-event webinar info'
    )

    language = fields.Many2one(
        comodel_name='res.lang',
        string='Language'
    )

    extra_info = fields.Text(
        string='Extra info',
    )

    returning_speaker = fields.Boolean(
        string='Has been a speaker at an earlier event',
        default=False,
    )

    # 3. Default methods

    # 4. Compute and search fields
    def _get_rating(self):
        for record in self:
            existing_rating = record.ratings.search([
                ('create_uid', '=', record.env.uid),
                ('event_track', '=', record.id),
            ])

            rating = 0
            if existing_rating:
                rating = existing_rating.rating

            record.rating = str(rating)

    def _set_rating(self):
        for record in self:
            existing_rating = record.ratings.search([
                ('create_uid', '=', record.env.uid),
                ('event_track', '=', record.id),
            ])

            if existing_rating:
                existing_rating.rating = record.rating
            else:
                rating = record.ratings.create({
                    'event_track': record.id,
                    'rating': record.rating,
                })

    def _compute_rating_avg(self):
        for record in self:
            if not record.ratings:
                continue

            ratings_sum = 0
            for rating in record.ratings:
                ratings_sum += rating.rating

            avg = ratings_sum / len(record.ratings)

            record.rating_avg = avg

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, values):
        values['description_original'] = values.get('description')

        return super(EventTrack, self).create(values)

    @api.multi
    def write(self, values):
        # Save a diff in messages when the description is changed
        if values.get('description'):
            self.create_diff(values)

        # Force field access rights
        allowed_fields = set(['description', 'rating'])
        disallowed_fields = set(values.keys()) - allowed_fields

        if disallowed_fields and not self.env.user.has_group('event.group_event_manager'):
            raise AccessError(_("You don't have a permission to write fields %s") % disallowed_fields)

        res = super(EventTrack, self).write(values)

        # Update followers
        if 'review_group' in values:
            # Remove all old followers
            for follower in self.message_follower_ids:
                self.message_unsubscribe([follower.partner_id.id])

            if values.get('review_group'):
                # Add new followers
                for partner in self.review_group.reviewers:
                    self.message_subscribe([partner.id])

        return res

    # 7. Action methods

    # 8. Business methods
    def create_diff(self, values):
        old_desc = html2plaintext(self.description).splitlines()
        new_desc = html2plaintext(values['description']).splitlines()

        d = difflib.Differ()
        diff = d.compare(old_desc, new_desc)

        diff_msg = ''

        for line in diff:
            code = line[:2]
            text = line[2:]

            if code in ['+ ', '- ']:
                if code == '+ ':
                    line_number = new_desc.index(text)
                    css_style = 'color: #0275d8;'
                else:
                    line_number = old_desc.index(text)
                    css_style = 'color: #636c72;'

                line_number += 1

                if not text.isspace() and text.strip() != '':
                    diff_msg += '<span style="%s">%s: %s</span><br/>' % (css_style, line_number, text)

        if diff_msg != '':
            subject = _('Content modified')

            body = '<strong>' + subject + '</strong><br/>' + \
                   '<p>' + diff_msg + '</p>'

            self.message_post(
                subject=subject,
                body=body,
            )