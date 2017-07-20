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

        print post
        values = self._get_event_track_proposal_post_values(event, **post)
        print values

        partner = request.env['res.partner'].sudo().create(values['contact'])
        track = request.env['event.track'].sudo().create(values['track'])

        print partner
        print track

        raise Exception("Not yet!")

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

    def _get_event_track_proposal_post_values(self, event, **post):
        # Contact
        contact_name = "%s %s" % (post['contact_last_name'], post['contact_first_name'])
        contact_values = {
            'name': contact_name,
            'email': post.get('contact_email'),
            'phone': post.get('contact_phone'),
            'zip': post.get('contact_zip'),
            'city': post.get('contact_city'),
            'organization': post.get('contact_organization'),
            'function': post.get('contact_title'),
        }

        # Track
        tags = []
        for tag in event.allowed_track_tag_ids:
            if post.get('tag_' + str(tag.id)):
                tags.append(tag.id)
        track_values = {
            'name': post.get('track_name'),
            'event_id': event.id,
            'tag_ids': [(6, 0, tags)],
            'user_id': False,
            'description': escape(post.get('description')),

            'video_url': post.get('video_url'),
            'webinar': post.get('webinar'),
            'webinar_info': post.get('webinar_info'),
            'returning_speaker': post.get('returning_speaker'),

            'extra_info': post.get('extra_info'),

            'target_group': post.get('target_group'),
            'target_group_info': post.get('target_group_info'),
            'language': post.get('language'),
        }

        values = {
            'contact': contact_values,
            'track': track_values,
        }

        return values