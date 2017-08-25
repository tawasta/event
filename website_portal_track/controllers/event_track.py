# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, _
from odoo.http import request

# 4. Imports from Odoo modules (rarely, and only if necessary):
from odoo.addons.website_portal.controllers.main import website_account

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in


class WebsiteEventTrack(website_account):

    @http.route()
    def account(self, **kw):
        """ Add track documents to main account page """
        response = super(WebsiteEventTrack, self).account(**kw)
        partner = request.env.user.partner_id

        # TODO: remove sudo
        EventTrack = request.env['event.track'].sudo()
        track_count = EventTrack.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        ])

        response.qcontext.update({
            'track_count': track_count,
        })
        return response

    @http.route(
        ['/my/tracks', '/my/tracks/page/<int:page>'],
        type='http',
        auth='user',
        website=True,
    )
    def portal_my_tracks(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        # TODO: remove sudo
        EventTrack = request.env['event.track'].sudo()

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
