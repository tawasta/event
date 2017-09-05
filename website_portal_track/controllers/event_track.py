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
        # Reviewers get their own save
        if request.env.user.has_group('event.group_track_reviewer'):
            values = dict()
            values['rating'] = post.get('rating')
            values['rating_comment'] = post.get('rating_comment')
        else:
            values = WebsiteEventTrackController._get_event_track_proposal_post_values(
                WebsiteEventTrackController(),
                track.event_id,
                **post
            )['track']

        track.write(values)

        return request.redirect('/my/tracks/')

    # Confirm track
    @http.route(
        ['/my/tracks/confirm/<model("event.track"):track>'],
        type='http',
        auth='user',
        website=True,
        methods=['POST'])
    def event_track_confirm(self, track, **post):

        track.sudo().write({'state': 'confirmed'})

        return request.redirect('/my/tracks/')
