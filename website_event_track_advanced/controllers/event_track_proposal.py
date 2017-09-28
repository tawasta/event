# -*- coding: utf-8 -*-

# 1. Standard library imports:
import base64
import logging

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, fields
from odoo.http import request

# 4. Imports from Odoo modules (rarely, and only if necessary):
from odoo.addons.website_event_track.controllers.main import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in
_logger = logging.getLogger(__name__)


class WebsiteEventTrackController(WebsiteEventTrackController):

    # Overrides the default event_track_proposal controller route
    @http.route()
    def event_track_proposal(self, event, **post):

        values = self._get_event_track_proposal_values()
        values['event'] = event

        return request.render(
            'website_event_track.event_track_proposal',
            values,
        )

    def _get_event_track_proposal_values(self):
        target_groups = request.env['event.track.target.group'].search([])
        types = request.env['event.track.type'].search_read([], ['id', 'code', 'name', 'description'])
        languages = request.env['res.lang'].search([], order='id')
        track = request.env['event.track']

        values = {
            'target_groups': target_groups,
            'languages': languages,
            'types': types,
            'track': track,
        }

        return values

    # Overrides the default website_event_track controller route
    @http.route()
    def event_track_proposal_post(self, event, **post):
        # TODO: remove this "debug"
        _logger.info("Posted values: %s" % dict(post))

        # 1. Get the posted values in separate dicts
        values = self._get_event_track_proposal_post_values(event, **post)
        followers = list()

        # 2. Create user and contact (partner)
        user = False
        partner = False
        if values.get('contact') and values.get('contact').get('name'):
            user = self._create_signup_user(values.get('contact'))
            partner = user.partner_id

            followers.append(partner.id)
            values['track']['partner_id'] = partner.id

        # 3. Add contact to organization
        if values.get('contact_organization'):
            organization = self._create_organization(values.get('contact_organization'))

            # Add contact to the existing organization
            if partner:
                partner.parent_id = organization.id

        # 4. Add speakers
        speakers = list()
        for speaker in values.get('speakers'):
            # If user already exists, create a new partner
            existing_user = request.env['res.users'].sudo().search([('login', '=', speaker.get('email'))])

            # Get or create organization
            if speaker.get('organization'):
                organization = self._create_organization({'name': speaker.get('organization')})
                del speaker['organization']
                speaker['parent_id'] = organization.id

            if existing_user:
                new_speaker = request.env['res.partner'].sudo().create(speaker)
                followers.append(existing_user.partner_id.id)

            if not existing_user:
                new_speaker = self._create_signup_user(speaker).partner_id

            followers.append(new_speaker.id)
            speakers.append(new_speaker.id)

        values['track']['speaker_ids'] = [(6, 0, speakers)]

        # 5. Add workshop organization
        workshop_organizer = False
        if values.get('workshop_organizer'):
            workshop_organizer = self._create_organization(values.get('workshop_organizer'))

            values['track']['organizer'] = workshop_organizer.id

        # 6. Add organizer contact
        if values.get('workshop_signee') and values.get('workshop_signee').get('name'):
            if workshop_organizer:
                values['workshop_signee']['parent_id'] = workshop_organizer.id

            signee = request.env['res.partner'].sudo().create(values['workshop_signee'])
            values['track']['organizer_contact'] = signee.id

        # 7. Create the track
        track = request.env['event.track'].sudo().create(values['track'])

        # 8. Create an attachment
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

        # 9. Subscribe followers
        track.sudo().message_subscribe(partner_ids=followers)

        # 10. Check if we want to confirm the track
        if post.get('track-confirm') and post.get('track-confirm') != '':
            track.state = 'confirmed'

        # 11. Return
        return request.render('website_event_track.event_track_proposal_success', {'track': track, 'event': event})

    def _get_event_track_proposal_post_values(self, event, **post):
        # Organization
        contact_organization_values = {
            'name': post.get('contact_organization'),
            'type': 'invoice',
        }

        # Contact
        name = "%s %s" % (post.get('contact_last_name'), post.get('contact_first_name'))
        contact_values = {
            'name': name,
            'login': post.get('contact_email'),
            'email': post.get('contact_email'),
            'phone': post.get('contact_phone'),
            'zip': post.get('contact_zip'),
            'city': post.get('contact_city'),
            'function': post.get('contact_title'),
        }

        # Tags
        tags = []
        for tag in event.allowed_track_tag_ids:
            if post.get('tag_' + str(tag.id)):
                tags.append(tag.id)

        if post.get('keywords'):
            event_track_tag = request.env['event.track.tag']
            keyword = post.get('keywords').strip()
            tag = event_track_tag.search([('name', '=ilike', keyword)], limit=1)

            if not tag:
                tag = event_track_tag.sudo().create({'name': keyword})

            tags.append(tag.id)

        # Application type
        application_type = False
        if post.get('application_type'):
            event_track_type = request.env['event.track.type'].search([
                ('code', '=', post.get('application_type'))
            ], limit=1,
            )
            if event_track_type:
                application_type = event_track_type.id

        # Track
        track_values = {
            'name': post.get('track_name'),
            'type': application_type,
            'event_id': event.id,
            'keywords': post.get('keywords'),
            'tag_ids': [(6, 0, tags)],
            'user_id': False,
            'description': post.get('track_content'),

            'video_url': post.get('video_url'),
            'webinar': post.get('webinar') not in ['0', 'false'],
            'webinar_info': post.get('webinar_info'),

            'extra_info':post.get('extra_info'),

            'target_group': post.get('target_group'),
            'target_group_info': post.get('target_group_info'),

            'workshop_participants': post.get('workshop_participants'),
            'workshop_goals': post.get('workshop_goals'),
            'workshop_schedule': post.get('workshop_schedule'),
            'workshop_fee': post.get('workshop_fee'),
        }

        if post.get('language') and post.get('language') != '0':
            track_values['language'] = post.get('language')

        # Speakers
        speaker_values = list()
        if post.get('speakers_input_index'):
            for speaker_index in range(0, int(post.get('speakers_input_index'))+1):
                first_name = post.get('speaker_first_name[%s]' % speaker_index)
                last_name = post.get('speaker_last_name[%s]' % speaker_index)

                if not first_name or not last_name:
                    continue

                name = "%s %s" % (last_name,first_name)

                speaker_values.append({
                    'name': name,
                    'email': post.get('speaker_email[%s]' % speaker_index),
                    'zip': post.get('speaker_zip[%s]' % speaker_index),
                    'city': post.get('speaker_city[%s]' % speaker_index),
                    'organization': post.get('speaker_organization[%s]' % speaker_index),
                    'function': post.get('speaker_function[%s]' % speaker_index),
                })

        # Workshop
        workshop_organizer_values = {
            'name': post.get('organizer_organization'),
            'street': post.get('organizer_street'),
            'zip': post.get('organizer_zip'),
            'city': post.get('organizer_city'),
            'comment': post.get('organizer_business_id'),
            'ref': post.get('organizer_reference'),
            'type': 'invoice',
        }

        name = "%s %s" % (post.get('signee_last_name'), post.get('signee_first_name'))
        name = name.strip()
        workshop_signee_values = {
            'name': name,
            'email': post.get('signee_email'),
            'function': post.get('signee_title'),
        }

        values = {
            'contact_organization': contact_organization_values,
            'contact': contact_values,
            'track': track_values,
            'speakers': speaker_values,
            'workshop_organizer': workshop_organizer_values,
            'workshop_signee': workshop_signee_values,
        }

        return values

    def _create_signup_user(self, partner_values):
        user = request.env['res.users'].sudo().search([
            ('login', '=', partner_values.get('email'))
        ])

        if not user:
            if not partner_values.get('login') and partner_values.get('email'):
                partner_values['login'] = partner_values.get('email')

            user = request.env['res.users'].sudo()._signup_create_user(partner_values)
            user.with_context({'create_user': True}).action_reset_password()

        return user

    def _create_organization(self, organization_values):
        organization_name = organization_values.get('name')
        organization = request.env['res.partner'].search([
            ('name', '=ilike', organization_name)
        ], limit=1)

        if not organization:
            # Organization doesn't exists. Create one
            organization = request.env['res.partner'].sudo().create(organization_values)

        return organization
