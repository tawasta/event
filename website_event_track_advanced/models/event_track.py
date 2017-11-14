# -*- coding: utf-8 -*-

# 1. Standard library imports:
import difflib

# 2. Known third party imports:
from bs4 import BeautifulSoup

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

    organizer = fields.Many2one(
        comodel_name='res.partner',
        string='Organizer',
    )

    organizer_contact = fields.Many2one(
        comodel_name='res.partner',
        string='Organizer contact',
    )

    attachment_ids = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name='res_id',
        domain=[('res_model', '=', 'event.track')],
        string='Attachments',
    )

    description_plain = fields.Char(
        string='Plain description',
        compute='compute_description_plain',
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
        index=True,
        string='Rating',
        compute='_get_rating',
        inverse='_set_rating',
    )
    rating_comment = fields.Char(
        string='Verbal rating',
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
        string='Average rating',
        compute='_compute_rating_avg',
        store=True,
        copy=False,
    )

    target_group = fields.Many2one(
        comodel_name='event.track.target.group',
        relation='event_track',
        string='Target group',
    )

    target_group_info = fields.Html(
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
    webinar_info = fields.Html(
        string='Pre-event webinar info'
    )

    language = fields.Many2one(
        comodel_name='res.lang',
        string='Language'
    )

    keywords = fields.Text(
        string='Keywords',
        help='A free text key words',
    )

    extra_info = fields.Html(
        string='Extra info',
    )

    workshop_goals = fields.Html(
        string='Goals',
    )

    workshop_schedule = fields.Html(
        string='Schedule',
    )

    workshop_participants = fields.Integer(
        string='Max participants',
    )

    workshop_fee = fields.Text(
        string='Workshop participation fee',
        help='Leave empty for free workshops',
    )

    partner_string = fields.Text(
        string='Partner',
        compute='_compute_partner_string',
    )

    speakers_string = fields.Text(
        string='Speakers',
        compute='_compute_speakers_string',
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
            rating_comment = False
            if existing_rating:
                rating = existing_rating.rating
                rating_comment = existing_rating.comment

            record.rating = str(rating)
            record.rating_comment = rating_comment

    def _set_rating(self):
        for record in self:
            existing_rating = record.ratings.search([
                ('create_uid', '=', record.env.uid),
                ('event_track', '=', record.id),
            ])

            if existing_rating:
                existing_rating.rating = self.rating
                existing_rating.comment = self.rating_comment
            else:
                rating = record.ratings.create({
                    'event_track': self.id,
                    'rating': self.rating,
                    'rating_comment': self.rating_comment,
                })

    @api.depends('ratings', 'ratings.rating')
    def _compute_rating_avg(self):
        for record in self:
            if not record.ratings:
                continue

            ratings_sum = 0
            for rating in record.ratings:
                ratings_sum += rating.rating

            avg = float(ratings_sum) / float(len(record.ratings))

            record.rating_avg = avg

    def _compute_partner_string(self):
        for record in self:
            record.partner_string = record.partner_id.name

    def _compute_speakers_string(self):
        for record in self:
            speakers = ''
            for speaker in record.speaker_ids:
                speakers += " %s," % speaker.name

            speakers = speakers[1:-1]

            record.speakers_string = speakers

    @api.multi
    @api.depends('description')
    def compute_description_plain(self):
        for record in self:
            record.description_plain = BeautifulSoup(record.description).text

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

        '''
        # Force field access rights
        allowed_fields = set(['description', 'rating', 'rating_comment', 'tag_ids', 'target_group_info'])
        disallowed_fields = set(values.keys()) - allowed_fields

        if disallowed_fields and not self.env.user.has_group('event.group_event_manager'):
            raise AccessError(_("You don't have a permission to write fields %s") % disallowed_fields)
        '''

        # Update followers
        if 'review_group' in values:
            # Remove all old followers
            for follower in self.review_group.reviewers:
                self.message_unsubscribe([follower.id])

            if values.get('review_group'):
                # Add new followers
                review_group = self.env['event.track.review.group'].browse([values.get('review_group')])
                for partner in review_group.reviewers:
                    self.message_subscribe([partner.id])

        res = super(EventTrack, self).write(values)

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