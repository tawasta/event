# -*- coding: utf-8 -*-

# 1. Standard library imports:
import base64

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, fields
from odoo.http import request
from odoo.tools import html_escape as escape, html2plaintext

# 4. Imports from Odoo modules (rarely, and only if necessary):
from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in


class WebsiteEventTrackController(WebsiteEventTrackController):

    # Overrides the default event_track_proposal controller route
    @http.route()
    def event_track_proposal(self, event, **post):

        target_groups = request.env['event.track.target.group'].search([])
        languages = request.env['res.lang'].search([])

        return request.render(
            "website_event_track.event_track_proposal",
            {
                'event': event,
                'target_groups': target_groups,
                'languages': languages,
            },
        )

    # Overrides the default website_event_track controller route
    @http.route()
    def event_track_proposal_post(self, event, **post):
        tags = []
        for tag in event.allowed_track_tag_ids:
            if post.get('tag_' + str(tag.id)):
                tags.append(tag.id)

        values = {
            'name': post['track_name'],
            'partner_name': post['partner_name'],
            'partner_email': post['email_from'],
            'partner_phone': post['phone'],
            'partner_biography': escape(post['biography']),
            'event_id': event.id,
            'tag_ids': [(6, 0, tags)],
            'user_id': False,
            'description': escape(post['description']),
        }

        track = request.env['event.track'].sudo().create(values)

        # Create attachment
        # TODO: could this be done in the track create?
        # TODO: multiple attachments?
        attachment_values = {
            'name': post['attachment_ids'].filename,
            'datas': base64.encodestring(post['attachment_ids'].read()),
            'datas_fname': post['attachment_ids'].filename,
            'res_model': 'event.track',
            'res_id': track.id,
            'type': 'binary'
        }
        attachment = request.env['ir.attachment'].sudo().create(attachment_values)

        if request.env.user != request.website.user_id:
            track.sudo().message_subscribe_users(user_ids=request.env.user.ids)
        else:
            partner = request.env['res.partner'].sudo().search([('email', '=', post['email_from'])])
            if partner:
                track.sudo().message_subscribe(partner_ids=partner.ids)

        return request.render("website_event_track.event_track_proposal_success", {'track': track, 'event': event})
