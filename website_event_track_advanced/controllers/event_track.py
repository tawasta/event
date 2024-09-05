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
import json
import logging
import sys

# 2. Known third party imports:
from psycopg2.errors import InvalidTextRepresentation
from werkzeug.exceptions import NotFound

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
    def _prepare_calendar_values(self, event):
        """
        sort locations based on sequence
        """
        res = super(EventTrackControllerAdvanced, self)._prepare_calendar_values(event)
        res.get("locations").sort(key=lambda x: x.sequence)
        return res

    def _get_event_track_proposal_values(self, event):
        partner_id = request.env.user.partner_id
        track_languages = request.env["res.lang"].search([], order="id")
        tracks = (
            request.env["event.track"]
            .sudo()
            .search([["partner_id", "=", partner_id.id], ["event_id", "=", event.id]])
        )

        values = {
            "tracks": tracks,
            "event": event,
            "main_object": event,
            "track_languages": track_languages,
        }
        return values

    @http.route(
        ["/event/track/data"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_track(self, track_id, isReview=False, **kwargs):
        logging.info("=====FUNKTIO=====")
        track = request.env["event.track"].sudo().browse(track_id)

        user = request.env.user
        can_review = False

        values = {}

        if isReview:
            if user.id in track.review_group.reviewers.mapped("user_id").ids:
                can_review = True
                rating_grade_ids = [
                    {
                        "id": rating.id,
                        "name": rating.name,
                    }
                    for rating in track.event_id.rating_grade_ids
                ]

                reviewer_id = (
                    request.env["event.track.reviewer"]
                    .sudo()
                    .search([("user_id", "=", user.id)])
                )
                user_rating = (
                    request.env["event.track.rating"]
                    .sudo()
                    .search(
                        [
                            ("event_track", "=", track.id),
                            ("reviewer_id", "=", reviewer_id.id),
                        ]
                    )
                )
                if user_rating:
                    rating = user_rating.grade_id.id
                    rating_comment = user_rating.comment

                    values.update({"rating": rating, "rating_comment": rating_comment})
                values.update(
                    {
                        "can_review": can_review,
                        "rating_grade_ids": rating_grade_ids,
                    }
                )

            if not can_review:
                return {"error": "You do not have permission to review this track."}

        # Tarkista, onko nykyinen vaihe is_submitted = True
        is_readonly = not track.stage_id.is_editable

        speakers = []
        for speaker in sorted(track.speaker_ids, key=lambda s: s.id):
            speakers.append(
                {
                    "id": speaker.id,
                    "firstname": speaker.firstname or "",
                    "lastname": speaker.lastname or "",
                    "email": speaker.email or "",
                    "phone": speaker.phone or "",
                    "organization": speaker.parent_id.name if speaker.parent_id else "",
                    "title": speaker.function or "",
                }
            )
        application_types = [
            {
                "id": app_type.id,
                "name": app_type.name,
                "workshop": app_type.workshop,
                "workshop_contract": app_type.workshop_contract,
                "webinar": app_type.webinar,
                "description": app_type.description or "",
            }
            for app_type in track.event_id.track_types_ids
        ]

        request_time = [
            {"id": req.id, "name": req.name}
            for req in request.env["event.track.request.time"].sudo().search([])
        ]
        target_groups = [
            {"id": group.id, "name": group.name}
            for group in track.event_id.target_group_ids
        ]

        tags = [
            {"id": tag.id, "name": tag.name}
            for tag in track.event_id.allowed_track_tag_ids
        ]

        attachments = [
            {"id": attachment.id, "name": attachment.name}
            for attachment in track.attachment_ids
        ]

        languages = [
            {
                "id": lang.id,
                "name": lang.name,
            }
            for lang in request.env["res.lang"].sudo().search([])
        ]

        # Get privacy settings and already accepted privacy
        privacy_ids = []
        accepted_privacies = (
            request.env["privacy.consent"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", track.partner_id.id),
                    ("activity_id", "in", track.event_id.privacy_ids.ids),
                ]
            )
        )

        for privacy in track.event_id.privacy_ids:
            privacy_ids.append(
                {
                    "id": privacy.id,
                    "name": privacy.name,
                    "link": privacy.link,
                    "link_name": privacy.link_name,
                    "is_required": privacy.is_required,
                    "accepted": privacy.id
                    in accepted_privacies.mapped("activity_id.id"),
                }
            )

        values.update(
            {
                "track_id": track.id,
                "name": track.name,
                "description": track.description,
                "type": track.type.id,
                "video_url": track.video_url,
                "language": track.language.id,
                "languages": languages,
                "target_group_ids": track.target_group_ids.ids,
                "target_group_info": track.target_group_info,
                "tag_ids": track.tag_ids.ids,
                "extra_info": track.extra_info,
                "partner_id": [track.partner_id.id, track.partner_id.name]
                if track.partner_id
                else "",
                "contact": {
                    "id": track.partner_id.id,
                    "firstname": track.partner_id.firstname or "",
                    "lastname": track.partner_id.lastname or "",
                    "email": track.partner_id.email or "",
                    "phone": track.partner_id.phone or "",
                    "organization": track.partner_id.parent_id.name
                    if track.partner_id.parent_id
                    else "",
                    "title": track.partner_id.function or "",
                },
                "speakers": speakers,
                "is_readonly": is_readonly,
                "application_types": application_types,
                "target_groups": target_groups,
                "tags": tags,
                "attachments": attachments,
                "privacy_ids": privacy_ids,
            }
        )

        # Lisätään workshop-tiedot vain jos track on tyyppiä workshop
        if track.type and track.type.workshop:
            values.update(
                {
                    "workshop_participants": track.workshop_participants,
                    "workshop_min_participants": track.workshop_min_participants,
                    "workshop_fee": track.workshop_fee,
                    "workshop_goals": track.workshop_goals,
                    "workshop_schedule": track.workshop_schedule,
                    "workshop_contract": track.type.workshop_contract,
                    "is_workshop": track.type.workshop,
                    "request_time": request_time,
                    "req_time": track.request_time.id,
                }
            )
            if track.organizer_contact:
                values.update(
                    {
                        "signee_firstname": track.organizer_contact.firstname,
                        "signee_lastname": track.organizer_contact.lastname,
                        "signee_email": track.organizer_contact.email,
                        "signee_phone": track.organizer_contact.phone,
                        "signee_organization": track.organizer_contact.parent_id.name,
                        "signee_title": track.organizer_contact.function,
                        "organizer_organization": track.organizer.name,
                        "organizer_street": track.organizer.street,
                        "organizer_zip": track.organizer.zip,
                        "organizer_city": track.organizer.city,
                        "edicode": track.organizer.edicode,
                        "organizer_reference": track.organizer.ref,
                    }
                )
            if track.stage_id.is_accepted:
                values.update(
                    {
                        "is_workshop_contract": True,
                    }
                )

        # Lisätään webinar-tiedot vain jos track on tyyppiä webinar
        if track.type and track.type.webinar:
            values.update(
                {
                    "webinar": track.webinar,
                    "webinar_info": track.webinar_info,
                }
            )
        logging.info("===VALUESIT===")
        logging.info(values)
        return values

    # @http.route(
    #     ["/event/speaker/remove"],
    #     type="json",
    #     auth="public",
    #     methods=["POST"],
    #     website=True,
    # )
    # def remove_speaker(self, speaker_id, **kwargs):
    #     speaker = request.env['res.partner'].browse(speaker_id)
    #     event = speaker.track_id
    #     logging.info(speaker.track_id.event_id.speaker_ids);
    #     if speaker_id:
    #         logging.info("===POISTETAAN=====");
    #         speaker.sudo().unlink()  # Poista rekordi tietokannasta

    #         logging.info(event.speaker_ids);
    #         return {
    #             "success": True,
    #         }

    @http.route(
        ["/event/application_types"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_application_types(self, event_id, **kwargs):
        event = request.env["event.event"].sudo().browse(event_id)

        application_types = [
            {
                "id": app_type.id,
                "name": app_type.name,
                "workshop": app_type.workshop,
                "workshop_contract": app_type.workshop_contract,
                "webinar": app_type.webinar,
                "description": app_type.description or "",
            }
            for app_type in event.track_types_ids
        ]

        request_time = [
            {"id": req.id, "name": req.name}
            for req in request.env["event.track.request.time"].sudo().search([])
        ]

        target_groups = [
            {"id": group.id, "name": group.name} for group in event.target_group_ids
        ]

        tags = [{"id": tag.id, "name": tag.name} for tag in event.allowed_track_tag_ids]

        languages = [
            {
                "id": lang.id,
                "name": lang.name,
            }
            for lang in request.env["res.lang"].sudo().search([])
        ]

        privacy_ids = [
            {
                "id": privacy.id,
                "name": privacy.name,
                "link": privacy.link,
                "link_name": privacy.link_name,
                "is_required": privacy.is_required,
            }
            for privacy in event.privacy_ids
        ]

        if request.env.user and not request.env.user._is_public():
            user = request.env.user

            # Lisätään käyttäjän yhteystiedot vastaukseen
            contact_info = {
                "firstname": user.partner_id.firstname,
                "lastname": user.partner_id.lastname,
                "email": user.partner_id.email or "",
                "phone": user.partner_id.phone or "",
                "organization": user.partner_id.parent_id.name or "",
                "title": user.partner_id.function or "",
                "contact_id": user.partner_id.id,
            }
        else:
            contact_info = {}

        return {
            "application_types": application_types,
            "target_groups": target_groups,
            "tags": tags,
            "request_time": request_time,
            "privacy_ids": privacy_ids,
            "languages": languages,
            "contact_info": contact_info,
        }

    def _get_event_track_proposal_form_values(self, event, **post):
        partner_id = request.env.user.partner_id
        reviewer_id = request.env.user.reviewer_id
        track_id = post.get("track_id")
        track_languages = request.env["res.lang"].search([], order="id")
        review = False
        editable = False
        existing_rating = False
        draft = False
        if track_id:
            track = request.env["event.track"].sudo().search([["id", "=", track_id]])
            if (
                reviewer_id
                and track.review_group
                and reviewer_id in track.review_group.reviewers
                and partner_id != track.partner_id
                and track.stage_id.is_submitted
            ):
                editable = False
                review = True
                existing_rating = (
                    request.env["event.track.rating"]
                    .sudo()
                    .search(
                        [
                            ["event_track", "=", track.id],
                            ["reviewer_id", "=", reviewer_id.id],
                        ]
                    )
                )
            elif track:
                editable = (
                    True
                    if partner_id == track.partner_id and track.stage_id.is_editable
                    else False
                )
                draft = True if track.stage_id.is_draft else False
        else:
            track = request.env["event.track"]
            editable = True
            draft = True
        _logger.debug(request.env.user)
        _logger.debug(request.env.ref("base.public_user"))
        values = {
            "track": track,
            "track_languages": track_languages,
            "event": event,
            "main_object": event,
            "editable": editable,
            "review": review,
            "draft": draft,
            "existing_rating": existing_rating,
            "partner": partner_id
            if request.env.user != request.env.ref("base.public_user")
            else False,
        }
        _logger.debug("Proposal form values:\n%s" % values)
        return values

    def _get_record(self, model, record_id):
        record_value = False
        if record_id:
            try:
                record = (
                    request.env[model].sudo().search([("id", "=", record_id)], limit=1)
                )
                if record:
                    record_value = record
            except InvalidTextRepresentation:
                _logger.warning(_("Integer expected for search: '%s'" % record_id))
        return record_value

    def _names_order_default(self):
        return "first_last"

    def _get_names_order(self):
        """Get names order configuration from system parameters.
        You can override this method to read configuration from language,
        country, company or other"""
        return (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("partner_names_order", self._names_order_default())
        )

    def _get_name(self, lastname, firstname):
        order = self._get_names_order()
        if order == "last_first_comma":
            return ", ".join(p for p in (lastname, firstname) if p)
        elif order == "first_last":
            return " ".join(p for p in (firstname, lastname) if p)
        else:
            return " ".join(p for p in (lastname, firstname) if p)

    def _get_event_track_proposal_post_values(self, event, **post):
        """Organize and validate post values

        :param dict post: post values from form
        :param event.event event: event for this event.track
        :return dict values: sorted post values
        """
        values = {}

        logging.info(post.get("contact_id"))
        # Contact
        contact_values = {
            "id": post.get("contact_id"),
            "lastname": post.get("contact_lastname").strip(),
            "firstname": post.get("contact_firstname").strip(),
            "name": self._get_name(
                post.get("contact_lastname").strip(),
                post.get("contact_firstname").strip(),
            ),
            "login": post.get("contact_email"),
            "email": post.get("contact_email"),
            "phone": post.get("contact_phone"),
            "function": post.get("contact_title"),
            "company_type": "person",
        }
        contact_organization_values = {
            "name": post.get("contact_organization"),
            "type": "invoice",
            "company_type": "company",
        }

        # Application type
        application_type = self._get_record("event.track.type", post.get("type"))

        # Target group
        if "target_group" in post and post.get("target_group"):
            target_group = self._get_record(
                "event.track.target.group", post.get("target_group")
            )
        else:
            pass

        # Tags/Keywords
        tags = False
        tag_post = request.httprequest.form.getlist("tags")
        _logger.debug("Tag list from post: %s" % tag_post)
        if tag_post and not "" in tag_post:
            tags = list(map(int, tag_post))

        # Target groups
        target_group_ids = False
        target_post = request.httprequest.form.getlist("target_groups")
        _logger.debug("Tag list from post: %s" % target_post)
        if target_post and not "" in target_post:
            target_group_ids = list(map(int, target_post))

        # Track
        track_id = self._get_record("event.track", post.get("track_id"))
        track_values = {
            "name": post.get("name"),
            "type": application_type.id if application_type else False,
            "event_id": event.id,
            "user_id": False,
            "description": post.get("description"),
            "video_url": post.get("video_url"),
            "extra_info": post.get("extra_info"),
            "target_group_ids": [(6, 0, target_group_ids)]
            if target_group_ids
            else False,
            "target_group_info": post.get("target_group_info"),
            "tag_ids": [(6, 0, tags)] if tags else False,
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
                        "id": post.get("speaker_id[%s]" % speaker_index),
                        "lastname": post.get(
                            "speaker_lastname[%s]" % speaker_index
                        ).strip(),
                        "firstname": post.get(
                            "speaker_firstname[%s]" % speaker_index
                        ).strip(),
                        "name": self._get_name(
                            post.get("speaker_lastname[%s]" % speaker_index).strip(),
                            post.get("speaker_firstname[%s]" % speaker_index).strip(),
                        ),
                        "email": post.get("speaker_email[%s]" % speaker_index),
                        "organization": post.get(
                            "speaker_organization[%s]" % speaker_index
                        ),
                        "function": post.get("speaker_title[%s]" % speaker_index),
                        "phone": post.get("speaker_phone[%s]" % speaker_index),
                        "company_type": "person",
                    }
                )

        # Webinar
        if post.get("is_webinar") and post.get("is_webinar") == "true":
            track_values["webinar"] = post.get("webinar")
            track_values["webinar_info"] = post.get("webinar_info")

        # Workshop
        if post.get("is_workshop") and post.get("is_workshop") == "true":
            track_values["workshop_participants"] = post.get("workshop_participants")
            track_values["workshop_min_participants"] = post.get(
                "workshop_min_participants"
            )
            track_values["workshop_goals"] = post.get("workshop_goals")
            track_values["workshop_schedule"] = post.get("workshop_schedule")
            track_values["workshop_fee"] = post.get("workshop_fee")

            if post.get("request_time"):
                request_time = self._get_record(
                    "event.track.request.time", post.get("request_time")
                )
                track_values["request_time"] = (
                    request_time.id if request_time else False,
                )

            if (
                post.get("is_workshop_contract")
                and post.get("is_workshop_contract") == "true"
            ):
                workshop_organizer_values = {
                    "name": post.get("organizer_organization"),
                    "street": post.get("organizer_street"),
                    "zip": post.get("organizer_zip"),
                    "city": post.get("organizer_city"),
                    "ref": post.get("organizer_reference"),
                    "einvoice_operator_id": post.get("einvoice_operator_id"),
                    "edicode": post.get("edicode"),
                    "type": "invoice",
                    "company_type": "company",
                }
                workshop_signee_values = {
                    "id": post.get("signee_id"),
                    "lastname": post.get("signee_lastname"),
                    "firstname": post.get("signee_firstname"),
                    "name": self._get_name(
                        post.get("signee_lastname"), post.get("signee_firstname")
                    ),
                    "email": post.get("signee_email"),
                    "phone": post.get("signee_phone"),
                    "function": post.get("signee_title"),
                    "company_type": "person",
                }
                values.update(
                    {
                        "workshop_organizer": workshop_organizer_values,
                        "workshop_signee": workshop_signee_values,
                    }
                )
        track_confirm = (
            True
            if post.get("track-confirm") and post.get("track-confirm") != ""
            else False
        )
        track_draft = (
            True if "track-draft" in post and post.get("track-draft") != "" else False
        )
        track_is_done = (
            True
            if "track-is-done" in post and post.get("track-is-done") != ""
            else False
        )
        values.update(
            {
                "contact_organization": contact_organization_values,
                "contact": contact_values,
                "track_id": track_id,
                "track": track_values,
                "speakers": speaker_values,
                "track_confirm": track_confirm,
                "track_draft": track_draft,
                "track_is_done": track_is_done,
            }
        )

        return values

    def _create_privacy(self, post, partner, event):
        """Create privacies"""
        privacy_ids = []
        for privacy in event.privacy_ids:
            if post.get("privacy_" + str(privacy.id)):
                privacy_ids.append(privacy.id)

        if privacy_ids:
            for pr in event.privacy_ids:
                accepted = pr.id in privacy_ids
                privacy_values = {
                    "partner_id": partner.id,
                    "activity_id": pr.id,
                    "accepted": accepted,
                    "state": "answered",
                }
                already_privacy_record = (
                    request.env["privacy.consent"]
                    .sudo()
                    .search(
                        [("partner_id", "=", partner.id), ("activity_id", "=", pr.id)]
                    )
                )
                if already_privacy_record:
                    already_privacy_record.sudo().write({"accepted": accepted})
                else:
                    request.env["privacy.consent"].sudo().create(privacy_values)

    def _create_signup_user(self, partner_values):
        """Find existing user by email. Update user if it is done by the user.
        If no user exists. Create a new user. Otherwise return existing user.

        :param dict partner_values: dictionary of values for partner
        :return res.users user: new or existing user
        """
        if not partner_values.get("id"):
            partner_values.pop("id", None)  # Poista 'id', jos se on olemassa ja tyhjä

        user = (
            request.env["res.users"]
            .sudo()
            .search([("login", "=ilike", partner_values.get("email"))])
        )
        user_exists = True
        # Only write values to user if it is done by the user.
        if user.id == request.env.user.id:
            user.sudo().write(partner_values)
            _logger.info(_("Updated user values for %s." % user))
        # If no user exists. Create a new user.
        elif not user:
            user_exists = False
            if not partner_values.get("login") and partner_values.get("email"):
                partner_values["login"] = partner_values.get("email")
            try:
                logging.info("==PARTNER VALUES===")
                logging.info(partner_values)
                user = (
                    request.env["res.users"].sudo()._signup_create_user(partner_values)
                )
                _logger.info(_("Created a new user %s." % user))
            except SignupError:
                _logger.warning(_("Signup is not allowed for uninvited users."))
                return False
            try:
                user.with_context({"create_user": True}).action_reset_password()
            except MailDeliveryException:
                _logger.warning(
                    _("Could not deliver mail to %s" % partner_values.get("email"))
                )

        return user, user_exists

    def _create_organization(self, organization_values):
        """Find existing user organization partner by name and update it
        or create a new organization partner

        :param dict organization_values: dictionary of values for organization partner
        :return res.partner organization: new or existing organization partner
        """
        organization_name = organization_values.get("name")
        if not organization_name or organization_name == "":
            _logger.warning(_("Could not create organization (missing name)"))
            return False

        organization = (
            request.env["res.partner"]
            .sudo()
            .search([("name", "=ilike", organization_name)], limit=1)
        )

        if not organization:
            organization_values["is_company"] = True
            organization = request.env["res.partner"].sudo().create(organization_values)
            _logger.info(_("Created a new organization %s." % organization))
        else:
            organization.sudo().write(organization_values)
            _logger.info(_("Updated organization values for %s." % organization))

        return organization

    def _create_partner(self, partner_values):
        """Create or update partner

        :param dict partner_values: dictionary of values for partner
        :return res.partner partner: new or existing partner
        """
        existing_partner = (
            request.env["res.partner"]
            .sudo()
            .search([("id", "=", partner_values.get("id"))])
        )
        # Create or get existing organization
        organization_name = partner_values.pop("organization", "")
        if organization_name:
            organization = self._create_organization(
                {"name": organization_name.strip()}
            )
            if organization:
                partner_values["parent_id"] = organization.id
        if existing_partner:
            existing_partner.sudo().write(partner_values)
            partner = existing_partner
            _logger.info(_("Updated partner values for %s." % existing_partner))
        else:
            partner = request.env["res.partner"].sudo().create(partner_values)
            _logger.info(_("Created a new partner %s." % partner))

        return partner

    def _create_speakers(self, speaker_values, followers):
        """Create or update each speaker and add them as followers and speakers

        :param dict speaker_values: dictionary of values for multiple speaker partners
        :param list followers: list of followers for event.track record
        :return list speakers: list of speaker partner ids
        :return list followers: list of followers for event.track record
        """
        speakers = list()
        for speaker in speaker_values:
            partner = self._create_partner(speaker)
            followers.append(partner.id)
            speakers.append(partner.id)
        return speakers, followers

    def _create_attachments(self, track):
        """Multiple attachments can be selected, but **post only gives the first one.
        We have to iterate the httprequest to access all sent attachments

        :param event.track track: track to save attachment to
        """
        files_dict = request.httprequest.files.getlist("attachment_ids")
        for attachment in files_dict:
            attachment_file = attachment.read()
            attachment_size = sys.getsizeof(attachment_file)
            max_size = 30 * 1024 * 1024
            if attachment_size > max_size:
                _logger.warning(
                    _("File %s is too large. Skipping..." % attachment_file.filename)
                )
            else:
                # Create attachment
                attachment_data = {
                    "name": attachment.filename,
                    "store_fname": attachment.filename,
                    "datas": base64.b64encode(attachment_file),
                    "description": "Track attachment",
                    "type": "binary",
                    "res_model": "event.track",
                    "res_id": track.id,
                }
                request.env["ir.attachment"].sudo().create(attachment_data)

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
        return request.render(
            "website_event_track_advanced.event_track_proposal_advanced", values
        )

    # @http.route(
    #     ["""/event/<model("event.event"):event>/track_proposal/form"""],
    #     type="http",
    #     auth="public",
    #     methods=["POST"],
    #     website=True,
    #     sitemap=False,
    # )
    # def event_track_proposal_form(self, event, **post):
    #     if not event.can_access_from_current_website():
    #         raise NotFound()

    #     values = self._get_event_track_proposal_form_values(event, **post)
    #     return (
    #         request.env["ir.ui.view"]
    #         .sudo()
    #         ._render_template(
    #             "website_event_track_advanced.event_track_application", values
    #         )
    #     )

    def _create_review(self, **post):
        reviewer_id = request.env.user.reviewer_id
        track_id = post.get("track_id")
        if reviewer_id and track_id:
            track = request.env["event.track"].sudo().search([["id", "=", track_id]])
            rating_id = (
                request.env["event.track.rating.grade"]
                .sudo()
                .search([("id", "=", post.get("rating"))])
            )
            vals = {
                "event_track": track.id,
                "reviewer_id": reviewer_id.id,
                "grade_id": rating_id.id,
                "comment": post.get("rating_comment"),
            }
            logging.info(vals)
            existing_rating = (
                request.env["event.track.rating"]
                .sudo()
                .search(
                    [
                        ["event_track", "=", track.id],
                        ["reviewer_id", "=", reviewer_id.id],
                    ]
                )
            )
            if existing_rating:
                existing_rating.sudo().write(vals)
            else:
                request.env["event.track.rating"].sudo().create(vals)

    # flake8: noqa: C901
    @http.route(
        ["/event/<model('event.event'):event>/track_proposal/post"],
        type="http",  # Muutettu JSON-tyyppiseksi
        auth="public",
        methods=["POST"],
        website=True,
    )
    def event_track_proposal_post(self, event, **post):
        if not event.can_access_from_current_website():
            return json.dumps({"error": "Access denied"})

        try:
            # If post is review. Create review and return confirmation
            if post.get("review-confirm"):
                self._create_review(**post)
                message = "Your review has been successfully saved."
                return json.dumps(
                    {"success": True, "message": message, "redirect": "/my/tracks"}
                )

            followers = list()
            _logger.info(_("Posted values: %s") % dict(post))

            # 1. Sort posted values
            values = self._get_event_track_proposal_post_values(event, **post)

            _logger.info(_("Used values: %s") % values)

            # 2. Create user and contact (partner)
            user = False
            partner = False
            user_exists = False
            if values.get("contact"):
                user, user_exists = self._create_signup_user(values.get("contact"))
                if user:
                    partner = user.partner_id
                    followers.append(partner.id)
                    values["track"]["partner_id"] = partner.id

                    self._create_privacy(post, partner, event)

            # 3. Add contact to organization
            if values.get("contact_organization"):
                organization = self._create_organization(
                    values.get("contact_organization")
                )
                # Add contact to the existing organization
                if partner and partner != organization:
                    partner.parent_id = organization.id

            # 4. Add speakers
            speakers, followers = self._create_speakers(
                values.get("speakers"), followers
            )
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
            if values.get("workshop_signee") and values.get("workshop_signee").get(
                "name"
            ):
                if workshop_organizer:
                    values["workshop_signee"]["parent_id"] = workshop_organizer.id

                signee = self._create_partner(values["workshop_signee"])
                values["track"]["organizer_contact"] = signee.id

            if values.get("track_draft"):
                draft_stage = (
                    request.env["event.track.stage"]
                    .sudo()
                    .search([("is_draft", "=", True)], limit=1)
                )
                if draft_stage:
                    values["track"]["stage_id"] = draft_stage.id

            # 7. Check if we want to confirm or set track as done
            # if values.get("track_confirm"):
            #     first_submitted_stage = (
            #         request.env["event.track.stage"]
            #         .sudo()
            #         .search([("is_submitted", "=", True)], order="sequence")
            #     )
            #     if first_submitted_stage:
            #         values["track"]["stage_id"] = first_submitted_stage[0].id

            if values.get("track_is_done"):
                first_is_done_stage = (
                    request.env["event.track.stage"]
                    .sudo()
                    .search([("is_submitted", "=", True)], order="sequence")
                )
                logging.info(first_is_done_stage)
                if first_is_done_stage:
                    values["track"]["stage_id"] = first_is_done_stage[0].id

            # 8. Create/Write the track
            create_track = False
            if values.get("track_id"):
                track = values.get("track_id")
                track.sudo().write(values["track"])
            else:
                create_track = True
                track = request.env["event.track"].sudo().create(values["track"])

            # 9. Subscribe followers
            track.sudo().message_subscribe(partner_ids=followers)
            # If track is created, manually trigger change to send mail to new followers
            if create_track:
                track.sudo()._message_track_post_template(changes="{'stage_id'}")

            # 10. Create attachments
            if post.get("attachment_ids"):
                self._create_attachments(track)

            # 11. Return
            return_vals = self._get_event_track_proposal_values(event)
            return_vals.update({"submitted": True})
            return_vals.update({"track": track})
            return_vals.update({"user_exists": user_exists})

            # 11. Create success message based on stage_id
            if track.stage_id.is_editable and track.stage_id.is_draft:
                message = "Your proposal is saved as a draft and will not be reviewed until it is submitted."
            elif track.stage_id.is_fully_accessible:
                message = "Your track is saved and confirmed as part of the event."
            else:
                message = (
                    "We will evaluate your proposition and get back to you shortly."
                )

            return json.dumps({"success": True, "message": message})

        except Exception as e:
            _logger.error(f"Error in track proposal post: {str(e)}")
            return json.dumps({"success": False, "message": str(e)})

        # return request.render(
        #     "website_event_track_advanced.event_track_proposal_advanced", return_vals
        # )

    @http.route(
        [
            """/event/<model("event.event"):event>/track""",
            """/event/<model("event.event"):event>/track/tag/<model("event.track.tag"):tag>""",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def event_tracks(self, event, tag=None, **searches):
        """Do not include break tracks in track list"""
        if not event.can_access_from_current_website():
            raise NotFound()

        render_vals = self._event_tracks_get_values(event, tag=tag, **searches)
        render_vals["tracks"] = render_vals.get("tracks").filtered(
            lambda p: p.type.code != "break"
        )
        indexes_to_del = []
        for track_by_day in render_vals.get("tracks_by_day"):
            track_by_day["tracks"] = track_by_day.get("tracks").filtered(
                lambda p: p.type.code != "break"
            )
            if not track_by_day["tracks"]:
                indexes_to_del.append(render_vals["tracks_by_day"].index(track_by_day))

        for i in sorted(indexes_to_del, reverse=True):
            del render_vals["tracks_by_day"][i]
        render_vals["tracks_live"] = render_vals.get("tracks_live").filtered(
            lambda p: p.type.code != "break"
        )
        render_vals["tracks_soon"] = render_vals.get("tracks_soon").filtered(
            lambda p: p.type.code != "break"
        )
        return request.render("website_event_track.tracks_session", render_vals)

    # Poster listing
    @http.route(
        [
            """/event/<model("event.event"):event>/poster""",
            """/event/<model("event.event"):event>/poster/tag/<model("event.track.tag"):tag>""",
        ],
        type="http",
        auth="public",
        website=True,
    )
    def event_track_poster(self, event, tag=None, **searches):
        """Only show poster tracks"""
        if not event.can_access_from_current_website():
            raise NotFound()

        render_vals = self._event_tracks_get_values(event, tag=tag, **searches)

        # Suodatetaan vain julkaistut esitykset
        published_tracks = render_vals.get("tracks").filtered(
            lambda t: t.stage_id.is_done == True
        )

        # Päivitetään render_vals suodatetuilla arvoilla
        render_vals["tracks"] = published_tracks

        render_vals["tracks"] = render_vals.get("tracks").filtered(
            lambda p: p.type.code == "poster" and p.stage_id.is_done == True
        )

        indexes_to_del = []
        for track_by_day in render_vals.get("tracks_by_day"):
            track_by_day["tracks"] = track_by_day.get("tracks").filtered(
                lambda p: p.type.code == "poster" and p.stage_id.is_done == True
            )
            if not track_by_day["tracks"]:
                indexes_to_del.append(render_vals["tracks_by_day"].index(track_by_day))

        for i in sorted(indexes_to_del, reverse=True):
            del render_vals["tracks_by_day"][i]
        render_vals["tracks_live"] = render_vals.get("tracks_live").filtered(
            lambda p: p.type.code == "poster" and p.stage_id.is_done == True
        )
        render_vals["tracks_soon"] = render_vals.get("tracks_soon").filtered(
            lambda p: p.type.code == "poster" and p.stage_id.is_done == True
        )
        return request.render("website_event_track.tracks_session", render_vals)

    @http.route(
        ["""/event/<model("event.event"):event>/track_reviews/form"""],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def event_track_reviews_form(self, event, **post):
        if not event.can_access_from_current_website():
            raise NotFound()
        try:
            track = (
                request.env["event.track"]
                .sudo()
                .search([["id", "=", post.get("track_id")]])
            )
        except Exception:
            return 404
        reviews = (
            request.env["event.track.rating"]
            .sudo()
            .search([["event_track", "=", track.id]])
        )
        values = {
            "track": track,
            "event": event,
            "reviews": reviews,
            "average_review": track.rating_avg,
        }
        return (
            request.env["ir.ui.view"]
            .sudo()
            ._render_template(
                "website_event_track_advanced.event_track_reviews", values
            )
        )
