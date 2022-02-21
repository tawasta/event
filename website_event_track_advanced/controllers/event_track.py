##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################
# 1. Standard library imports:
import base64
import logging

from werkzeug.exceptions import NotFound

# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import _, http
from odoo.http import request

from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

# 4. Imports from Odoo modules:
from odoo.addons.website_event_track.controllers.event_track import EventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)


class EventTrackControllerAdvanced(EventTrackController):
    def _get_event_track_proposal_values(self, event):
        user_id = request.env.user
        tracks = request.env["event.track"].search(
            [["user_id", "=", user_id.id], ["event_id", "=", event.id]]
        )
        values = {"tracks": tracks, "event": event}
        return values

    def _get_event_track_proposal_form_values(self, event, **post):
        track_id = post.get("track_id")
        if track_id:
            track = request.env["event.track"].search([["id", "=", track_id]])
        else:
            track = request.env["event.track"]
        track_languages = request.env["res.lang"].search([], order="id")
        values = {"track": track, "track_languages": track_languages, "event": event}
        return values

    def _get_event_track_proposal_post_values(self, event, **post):
        print("@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@")
        print(post)
        # Contact
        contact_values = {
            "firstname": post.get("contact_firstname"),
            "lastname": post.get("contact_lastname"),
            "login": post.get("contact_email"),
            "email": post.get("contact_email"),
            "phone": post.get("contact_phone"),
            "function": post.get("contact_title"),
        }
        contact_organization_values = {
            "name": post.get("contact_organization"),
            "type": "invoice",
        }
        # Application type
        application_type = False
        if post.get("type"):
            event_track_type = request.env["event.track.type"].search(
                [("code", "=", post.get("type"))], limit=1
            )
            if event_track_type:
                application_type = event_track_type.id
        # Track
        track_values = {
            "name": post.get("name"),
            "type": application_type,
            "event_id": event.id,
            "user_id": False,
            "description": post.get("description"),
            "video_url": post.get("video_url"),
            "webinar": post.get("webinar") not in ["0", "false"],
            "webinar_info": post.get("webinar_info"),
            "extra_info": post.get("extra_info"),
            "target_group": post.get("target_group") not in ["0", "", "false"] or False,
            "target_group_info": post.get("target_group_info"),
            "workshop_participants": post.get("workshop_participants"),
            "workshop_goals": post.get("workshop_goals"),
            "workshop_schedule": post.get("workshop_schedule"),
            "workshop_fee": post.get("workshop_fee"),
        }
        # Language
        if post.get("language") and post.get("language") != "0":
            track_values["language"] = post.get("language")
        # Speakers
        speaker_values = list()
        if post.get("speakers_input_index"):
            for speaker_index in range(1, int(post.get("speakers_input_index")) + 1):
                speaker_values.append(
                    {
                        "firstname": post.get("speaker_firstname[%s]" % speaker_index),
                        "lastname": post.get("speaker_lastname[%s]" % speaker_index),
                        "email": post.get("speaker_email[%s]" % speaker_index),
                        "organization": post.get(
                            "speaker_organization[%s]" % speaker_index
                        ),
                        "function": post.get("speaker_title[%s]" % speaker_index),
                        "phone": post.get("speaker_phone[%s]" % speaker_index),
                    }
                )
        # Workshop
        workshop_organizer_values = {
            "name": post.get("organizer_organization"),
            "street": post.get("organizer_street"),
            "zip": post.get("organizer_zip"),
            "city": post.get("organizer_city"),
            "ref": post.get("organizer_reference"),
            "type": "invoice",
            "business_id": post.get("organizer_business_id"),
            "edicode": post.get("organizer_edicode"),
        }
        workshop_signee_organization_values = {
            "name": post.get("signee_organization"),
            "type": "invoice",
        }
        workshop_signee_values = {
            "firstname": post.get("signee_last_name"),
            "lastname": post.get("signee_first_name"),
            "email": post.get("signee_email"),
            "phone": post.get("signee_phone"),
            "function": post.get("signee_title"),
        }
        values = {
            "contact_organization": contact_organization_values,
            "contact": contact_values,
            "track": track_values,
            "speakers": speaker_values,
            "workshop_organizer": workshop_organizer_values,
            "workshop_signee": workshop_signee_values,
            "workshop_signee_organization": workshop_signee_organization_values,
        }
        return values

    @http.route(
        ["""/event/<model("event.event"):event>/track_proposal"""],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def event_track_proposal(self, event, **post):
        if not event.can_access_from_current_website():
            raise NotFound()

        values = self._get_event_track_proposal_values(event)
        return request.render("website_event_track.event_track_proposal", values)

    @http.route(
        ["""/event/<model("event.event"):event>/track_proposal/form"""],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def event_track_proposal_form(self, event, **post):
        if not event.can_access_from_current_website():
            raise NotFound()

        values = self._get_event_track_proposal_form_values(event, **post)

        return request.env["ir.ui.view"]._render_template(
            "website_event_track_advanced.event_track_application", values
        )

    @http.route(
        ["""/event/<model("event.event"):event>/track_proposal/post"""],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def event_track_proposal_post(self, event, **post):
        if not event.can_access_from_current_website():
            raise NotFound()

        followers = list()
        _logger.info(_("Posted values: %s" % dict(post)))

        # 1. Sort posted values
        values = self._get_event_track_proposal_post_values(event, **post)
        _logger.info(_("Used values: %s" % values))

        # 2. Create user and contact (partner)
        user = False
        partner = False
        if values.get("contact") and values.get("contact").get("name"):
            user = self._create_signup_user(values.get("contact"))
            partner = user.partner_id

            followers.append(partner.id)
            values["track"]["partner_id"] = partner.id

        # 3. Add contact to organization
        if values.get("contact_organization"):
            organization = self._create_organization(values.get("contact_organization"))

            # Add contact to the existing organization
            if partner and partner != organization:
                partner.parent_id = organization.id

        # 4. Add speakers
        speakers = list()
        for speaker in values.get("speakers"):
            # If user already exists, create a new partner
            existing_user = (
                request.env["res.users"]
                .sudo()
                .search([("login", "=", speaker.get("email"))])
            )

            # Get or create organization
            if speaker.get("organization"):
                organization = self._create_organization(
                    {"name": speaker.get("organization")}
                )
                del speaker["organization"]
                speaker["parent_id"] = organization.id

            if existing_user:
                new_speaker = request.env["res.partner"].sudo().create(speaker)
                followers.append(existing_user.partner_id.id)

            if not existing_user:
                new_speaker = self._create_signup_user(speaker).partner_id

            followers.append(new_speaker.id)
            speakers.append(new_speaker.id)

        values["track"]["speaker_ids"] = [(6, 0, speakers)]

        # 5. Add workshop organization
        workshop_organizer = False
        if values.get("workshop_organizer"):
            workshop_organizer = self._create_organization(
                values.get("workshop_organizer")
            )

            if workshop_organizer:
                values["track"]["organizer"] = workshop_organizer.id

        # 6. Add organizer contact
        if values.get("workshop_signee") and values.get("workshop_signee").get("name"):
            if workshop_organizer:
                values["workshop_signee"]["parent_id"] = workshop_organizer.id

            signee = request.env["res.partner"].sudo().create(values["workshop_signee"])
            values["track"]["organizer_contact"] = signee.id

        # 7. Create the track
        track = request.env["event.track"].sudo().create(values["track"])

        # 8. Create attachments
        if post.get("attachment_ids"):
            # Multiple attachments can be selected,
            # but **post only gives the first one.
            # We have to iterate the httprequest to access all sent attachments
            files_dict = dict(request.httprequest.files)

            for attachment_file in files_dict["attachment_ids"]:
                attachment_file_value = attachment_file.value

                attachment_name = attachment_file_value.filename
                attachment_data = attachment_file_value.read()

                # Create attachment
                attachment_data = {
                    "name": attachment_name,
                    "datas_fname": attachment_name,
                    "datas": base64.b64encode(str(attachment_data)),
                    "description": "Track attachment",
                    "type": "binary",
                    "res_model": "event.track",
                    "res_id": track.id,
                }
                request.env["ir.attachment"].sudo().create(attachment_data)

        # 9. Subscribe followers
        track.sudo().message_subscribe(partner_ids=followers)

        # 10. Send mail to track proposer
        email_template = track.env.ref(
            "website_event_track_advanced.email_template_event_track_received"
        )
        email_template.send_mail(track.id)

        values = self._get_event_track_proposal_values(event)
        return request.render("website_event_track.event_track_proposal", values)

    def _create_signup_user(self, partner_values):
        user = (
            request.env["res.users"]
            .sudo()
            .search([("login", "=ilike", partner_values.get("email"))])
        )

        if not user:
            if not partner_values.get("login") and partner_values.get("email"):
                partner_values["login"] = partner_values.get("email")

            try:
                user = (
                    request.env["res.users"].sudo()._signup_create_user(partner_values)
                )
            except SignupError:
                _logger.warn(_("Signup is not allowed for uninvited users"))

            try:
                user.with_context({"create_user": True}).action_reset_password()
            except MailDeliveryException:
                _logger.warn(
                    _("Could not deliver mail to %s" % partner_values.get("email"))
                )

        return user

    def _create_organization(self, organization_values):
        organization_name = organization_values.get("name")
        if not organization_name or organization_name == "":
            _logger.warning(_("Could not create organization (missing name)"))
            return False

        organization = request.env["res.partner"].search(
            [("name", "=ilike", organization_name)], limit=1
        )

        if not organization:
            # Organization doesn't exists. Create one
            organization_values["is_company"] = True
            organization = request.env["res.partner"].sudo().create(organization_values)
        else:
            # Organization exists. Update it
            organization.sudo().write(organization_values)

        return organization
