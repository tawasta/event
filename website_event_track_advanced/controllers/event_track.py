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
        types = request.env['event.track.type'].search_read([], ['id', 'name', 'description'])
        languages = request.env['res.lang'].search([])

        return request.render(
            "website_event_track.event_track_proposal",
            {
                'event': event,
                'target_groups': target_groups,
                'languages': languages,
                'types': types,
            },
        )

    # Overrides the default website_event_track controller route
    @http.route()
    def event_track_proposal_post(self, event, **post):

        values = self._get_event_track_proposal_post_values(event, **post)

        user = request.env['res.users'].sudo()._signup_create_user(values['contact'])
        user.action_reset_password()
        partner = user.partner_id

        speakers = list()
        for speaker in values['speakers']:
            speaker_id = request.env['res.partner'].sudo().create(speaker)
            speakers.append(speaker_id.id)

        # Add new values to track
        values['track']['partner_id'] = partner.id
        values['track']['speaker_ids'] = [(6, 0, speakers)]

        track = request.env['event.track'].sudo().create(values['track'])

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
            partner = request.env['res.partner'].sudo().search([('email', '=', post['contact_email'])])
            if partner:
                track.sudo().message_subscribe(partner_ids=partner.ids)

        return request.render("website_event_track.event_track_proposal_success", {'track': track, 'event': event})

    def _get_event_track_proposal_post_values(self, event, **post):
        # Contact
        contact_name = "%s %s" % (post['contact_last_name'], post['contact_first_name'])
        contact_values = {
            'name': contact_name,
            'login': post.get('contact_email'),
            'email': post.get('contact_email'),
            'phone': post.get('contact_phone'),
            'zip': post.get('contact_zip'),
            'city': post.get('contact_city'),
            'comment': post.get('contact_organization'),  # TODO
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
            'description': post.get('track_content'),

            'video_url': post.get('video_url'),
            'webinar': int(post.get('webinar')),
            'webinar_info': post.get('webinar_info'),
            'returning_speaker': int(post.get('returning_speaker')),

            'extra_info':post.get('extra_info'),

            'target_group': post.get('target_group'),
            'target_group_info': post.get('target_group_info'),
            'language': post.get('language'),
        }

        if post.get('speakers_input_index'):
            speaker_values = list()
            for speaker_index in range(0, int(post.get('speakers_input_index'))):
                first_name = post.get('speaker_first_name[%s]' % speaker_index)
                last_name = post.get('speaker_last_name[%s]' % speaker_index)

                if not first_name or not last_name:
                    continue

                speaker_name = "%s %s" % (last_name, first_name)

                speaker_values.append({
                    'name': speaker_name,
                    'email': post.get('speaker_email[%s]' % speaker_index),
                    'zip': post.get('speaker_zip[%s]' % speaker_index),
                    'city': post.get('speaker_city[%s]' % speaker_index),
                    'comment': post.get('speaker_organization[%s]' % speaker_index),  # TODO
                    'function': post.get('speaker_function[%s]' % speaker_index),
                })

        values = {
            'contact': contact_values,
            'track': track_values,
            'speakers': speaker_values,
        }

        return values
