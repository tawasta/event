# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError

# 4. Imports from Odoo modules:
from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.website_event_track_advanced.controllers.event_track_proposal import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports


class WebsiteEventTrack(website_account):

    # Add track count to account main menu
    @http.route()
    def account(self, **kw):
        """ Add track documents to main account page """
        response = super(WebsiteEventTrack, self).account(**kw)
        partner = request.env.user.partner_id

        EventTrack = request.env['event.track']
        track_count = EventTrack.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        ])

        response.qcontext.update({
            'track_count': track_count,
        })
        return response

    # All tracks
    @http.route(
        ['/my/tracks', '/my/tracks/page/<int:page>'],
        type='http',
        auth='user',
        website=True,
    )
    def portal_my_tracks(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        EventTrack = request.env['event.track']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        ]
        archive_groups = self._get_archive_groups('event.track', domain)

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        track_count = EventTrack.search_count(domain)

        pager = request.website.pager(
            url="/my/tracks",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=track_count,
            page=page,
            step=self._items_per_page
        )

        tracks = EventTrack.search(domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'tracks': tracks,
            'page_name': 'track',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/tracks',
        })
        return request.render("website_portal_track.portal_my_tracks", values)

    # Single track
    @http.route(['/my/tracks/<int:track>'], type='http', auth='user', website=True)
    def tracks_followup(self, track=None, **kw):
        track = request.env['event.track'].browse([track])
        try:
            track.check_access_rights('read')
            track.check_access_rule('read')
        except AccessError:
            return request.render('website.403')

        target_groups = request.env['event.track.target.group'].search([])
        types = request.env['event.track.type'].search_read([], ['code', 'name', 'description'])
        languages = request.env['res.lang'].search([], order='name DESC')

        view_name = 'website_portal_track.tracks_followup'

        # Reviewers get their own view
        if request.env.user.has_group('event.group_track_reviewer'):
            view_name = 'website_portal_track.tracks_followup_reviewers'

        return request.render(
            view_name,
            {
                'event': track.event_id,
                'track': track,
                'target_groups': target_groups,
                'languages': languages,
                'types': types,
            },
        )

    # Save track modifications
    @http.route(
        ['/my/tracks/save/<model("event.track"):track>'],
        type='http',
        auth='user',
        website=True,
        methods=['POST'])
    def event_track_save(self, track, **post):
        values = dict()

        # Reviewers get their own save
        if request.env.user.has_group('event.group_track_reviewer'):
            track_values = dict()
            track_values['rating'] = post.get('rating')
            track_values['rating_comment'] = post.get('rating_comment')
        else:
            values = WebsiteEventTrackController._get_event_track_proposal_post_values(
                WebsiteEventTrackController(),
                track.event_id,
                **post
            )
            track_values = values['track']

        speaker_ids = list()
        speakers = list()
        for speaker in values.get('speakers', []):
            # If user already exists, create a new partner
            existing_user = request.env['res.users'].sudo().search([('login', '=', speaker.get('email'))])

            # Get or create organization
            if speaker.get('organization'):
                organization = WebsiteEventTrackController._create_organization(
                    WebsiteEventTrackController(),
                    {'name': speaker.get('organization')}
                )
                del speaker['organization']
                speaker['parent_id'] = organization.id

            if existing_user:
                new_speaker = request.env['res.partner'].sudo().create(speaker)

            if not existing_user:
                new_speaker = WebsiteEventTrackController._create_signup_user(
                    WebsiteEventTrackController(), speaker
                ).partner_id

            speaker_ids.append(new_speaker.id)
            speakers.append((4, new_speaker.id))

        track_values['speaker_ids'] = speakers

        track.write(track_values)
        track.sudo().message_subscribe(partner_ids=speaker_ids)

        return request.redirect('/my/tracks/')

    # Confirm track
    @http.route(
        ['/my/tracks/confirm/<model("event.track"):track>'],
        type='http',
        auth='user',
        website=True,
        methods=['GET'])
    def event_track_confirm(self, track, **post):

        track.state = 'confirmed'

        return request.redirect('/my/tracks/')

    # Cancel track
    @http.route(
        ['/my/tracks/cancel/<model("event.track"):track>'],
        type='http',
        auth='user',
        website=True,
        methods=['GET'])
    def event_track_cancel(self, track, **post):

        track.state = 'cancel'

    # Refuse track
    @http.route(
        ['/my/tracks/refuse/<model("event.track"):track>'],
        type='http',
        auth='user',
        website=True,
        methods=['GET'])
    def event_track_refuse(self, track, **post):

        track.state = 'refused'

        return request.redirect('/my/tracks/')

    # Open track (set to draft)
    @http.route(
        ['/my/tracks/open/<model("event.track"):track>'],
        type='http',
        auth='user',
        website=True,
        methods=['GET'])
    def event_track_open(self, track, **post):

        track.state = 'draft'

        return request.redirect('/my/tracks/')

    # Approve track
    @http.route(
        ['/my/tracks/approve/<model("event.track"):track>'],
        type='http',
        auth='user',
        website=True,
        methods=['GET'])
    def event_track_open(self, track, **post):

        track.state = 'published'

        return request.redirect('/my/tracks/')
