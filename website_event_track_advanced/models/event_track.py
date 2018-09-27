# -*- coding: utf-8 -*-

# 1. Standard library imports:
import difflib
import dateutil.parser
from datetime import datetime, timedelta

# 2. Known third party imports:
from bs4 import BeautifulSoup

# 3. Odoo imports:
from odoo import api, fields, models
from odoo import _
from odoo.tools import html2plaintext


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

    chairperson_id = fields.Many2one(
        comodel_name='res.partner',
        string='Chairperson',
        domain=[('is_company', '=', False)],
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

    application_file = fields.Binary(
        string='Application',
    )
    application_file_filename = fields.Char(
        string='Application filename',
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

    ratings_count = fields.Integer(
        string='Ratings',
        compute='compute_ratings_count',
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

    date_end = fields.Datetime(
        string='End date',
        compute='compute_date_end',
        readonly=True,
        store=True,
        copy=False,
    )

    show_in_agenda = fields.Boolean(
        string='Shown in agenda',
        compute='_compute_show_in_agenda',
    )

    overlapping_location_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping locations',
        compute='_compute_overlapping_location_track_ids',
        # store=True,
        # relation='event_track_location_overlapping_rel',
    )

    # Disabled for now. These are causing problems with other overlapping ids
    overlapping_chairperson_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping chairpersons',
        compute='_compute_overlapping_chairperson_track_ids',
        # store=True,
        # relation='event_track_speaker_overlapping_rel',
    )

    overlapping_speaker_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping speakers',
        compute='_compute_overlapping_speaker_track_ids',
        # store=True,
        # relation='event_track_speaker_overlapping_rel',
    )

    external_registration = fields.Char(
        string='External registration link',
    )

    twitter_hashtag = fields.Char(
        string='Twitter hashtag',
        compute='compute_twitter_hashtag',
        store=True,
        copy=False,
    )

    extra_materials = fields.Html(
        string='Extra materials',
        help='Extra materials (links etc.) that are shown in agenda',
    )

    extra_materials_plain = fields.Char(
        string='Plain extra_materials',
        compute='compute_extra_materials_plain',
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

    def compute_ratings_count(self):
        for record in self:
            record.ratings_count = len(record.ratings)

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
            if record.description:
                record.description_plain = \
                    BeautifulSoup(record.description, 'lxml').text
            else:
                record.description_plain = ''

    @api.multi
    @api.depends('extra_materials')
    def compute_extra_materials_plain(self):
        for record in self:
            if record.extra_materials:
                record.extra_materials_plain = \
                    BeautifulSoup(record.extra_materials, 'lxml').text
            else:
                record.extra_materials_plain = ''

    @api.multi
    @api.depends('location_id', 'type')
    def _compute_show_in_agenda(self):
        for record in self:
            location_show = record.location_id.show_in_agenda \
                            or not record.location_id

            type_show = record.type.show_in_agenda

            show = location_show and type_show

            record.show_in_agenda = show

    @api.depends('date', 'duration')
    def compute_date_end(self):
        for record in self:
            if record.date and record.duration:
                end_date = dateutil.parser.parse(record.date) + timedelta(hours=record.duration)
                record.date_end = end_date

    # @api.onchange('date', 'duration', 'location_id')
    def _compute_overlapping_location_track_ids(self):
        # Search overlapping tracks in the same location

        EventTrack = self.env['event.track']
        for record in self:
            if not record.location_id \
                    or not record.date \
                    or not record.duration:
                # If all the necessary information is not set, skip this
                continue

            domain = list()

            if not isinstance(record.id, models.NewId):
                # Exclude the record itself
                domain.append(('id', '!=', record.id))

            domain += [
                # Same location
                ('location_id', '!=', False),
                ('location_id', '=', record.location_id.id),
                # Starts before this ends
                ('date', '<', record.date_end),
                # Ends after this starts
                ('date_end', '>', record.date),
            ]

            overlapping_tracks = EventTrack.search(domain)

            overlapping_tracks = overlapping_tracks.filtered(
                lambda t: t.id != record.id
            )

            if overlapping_tracks:
                record.overlapping_location_track_ids = \
                    overlapping_tracks.ids

    # @api.onchange('date', 'duration', 'chairperson_id')
    def _compute_overlapping_chairperson_track_ids(self):
        # Search overlapping tracks with same chairperson

        EventTrack = self.env['event.track']
        for record in self:
            if not record.chairperson_id \
                    or not record.date \
                    or not record.duration:
                # If all the necessary information is not set, skip this
                continue

            domain = list()

            if not isinstance(record.id, models.NewId):
                # Exclude the record itself
                domain.append(('id', '!=', record.id))

            domain += [
                # Same chairperson
                ('chairperson_id', '!=', False),
                ('chairperson_id', '=', record.chairperson_id.id),
                # Starts before this ends
                ('date', '<', record.date_end),
                # Ends after this starts
                ('date_end', '>', record.date),
            ]

            overlapping_tracks = EventTrack.search(domain)

            if overlapping_tracks:
                record.overlapping_chairperson_track_ids = \
                    overlapping_tracks.ids

    # @api.onchange('date', 'duration', 'speaker_ids')
    def _compute_overlapping_speaker_track_ids(self):
        # Search overlapping tracks with same speakers

        EventTrack = self.env['event.track']
        for record in self:
            if not record.speaker_ids \
                    or not record.date \
                    or not record.duration:
                # If all the necessary information is not set, skip this
                continue

            domain = list()

            if not isinstance(record.id, models.NewId):
                # Exclude the record itself
                domain.append(('id', '!=', record.id))

            domain += [
                # Same speaker
                ('speaker_ids', 'in', record.speaker_ids.ids),
                # Starts before this ends
                ('date', '<', record.date_end),
                # Ends after this starts
                ('date_end', '>', record.date),
            ]

            overlapping_tracks = EventTrack.search(domain)

            if overlapping_tracks:
                record.overlapping_speaker_track_ids = \
                    overlapping_tracks.ids

    @api.depends('type.twitter_hashtag')
    def compute_twitter_hashtag(self):
        # TODO: allow user to decide the format
        for record in self:
            if record.type.twitter_hashtag:
                hashtag = "%s%s" % (record.type.twitter_hashtag, record.id)

                record.twitter_hashtag = hashtag

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def create(self, values):
        values['description_original'] = values.get('description')
        res = super(EventTrack, self).create(values)

        '''
        depend_fields = ['date', 'duration', 'location_id']
        if set(depend_fields).intersection(set(values)):
            records = self.filtered(lambda t: t.type.code != 'break')
            records._calculate_breaks()
        '''

        return res

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

        '''
        depend_fields = ['date', 'duration', 'location_id']
        if set(depend_fields).intersection(set(values)):
            records = self.filtered(lambda t: t.type.code != 'break')
            records._calculate_breaks()
        '''

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

    def _calculate_breaks(self):
        # Auto-generate and auto-unlink breaks

        break_type = self.env.ref('event.event_track_type_break')
        track_model = self.env['event.track']

        for record in self:
            domain_filter = [
                '|',
                ('location_id', '=', record.location_id.id),
                ('location_id', '=', False),
                ('event_id', '=', record.event_id.id),
                ('website_published', '=', True),
                ('type.show_in_agenda', '=', True),
                ('date', '!=', False),
            ]

            if record.date:
                day_start = '%s 00:00:00' % record.date[0:10]
                day_end = '%s 23:59:59' % record.date[0:10]

                domain_filter.append(('date', '>=', day_start))
                domain_filter.append(('date', '<=', day_end))

            # Remove existing auto-generated breaks
            # While a bit counter-intuitive, this is less resource intense
            # than calculating overlapping breaks/tracks and shifting
            # existing breaks
            break_domain_filter = domain_filter[:]
            break_domain_filter.append(('type.code', '=', 'break'))
            break_domain_filter.append(('name', '=', ''))
            location_breaks = track_model.search(break_domain_filter)
            if location_breaks:
                location_breaks.unlink()

            # Search tracks for this location
            location_tracks = track_model.search(domain_filter, order='date')

            previous_track_end = False

            breaks = dict()
            for track in location_tracks:
                if track.type == break_type:
                    # Skip breaks
                    continue

                if not previous_track_end or track.date == previous_track_end:
                    # No break (the next track starts immediately)
                    previous_track_end = track.date_end
                    continue

                if previous_track_end[0:10] != track.date[0:10]:
                    # Different days. No break here
                    continue

                duration = abs(dateutil.parser.parse(track.date) -
                               dateutil.parser.parse(previous_track_end))
                duration = duration.total_seconds() / 3600

                # Empty slot between tracks. Create a break
                track_values = dict(
                    event_id=record.event_id.id,
                    location_id=record.location_id.id,
                    name='',
                    date=previous_track_end,
                    duration=duration,
                    type=break_type.id,
                    website_published=True,
                )

                previous_track_end = track.date_end
                track_model.create(track_values)

        # Recompute overlapping locations
        # self._compute_overlapping_location_track_ids()
