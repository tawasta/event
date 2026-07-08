##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
import json
import logging
from datetime import datetime, timedelta

# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class EventRegistrationSurvey(WebsiteEventSaleController):
    def _merge_survey_post_data(self, post):
        """Merge the JSON-encoded ``post-data`` field into a flat dict.

        The survey answers are posted as a single JSON-encoded ``post-data``
        field (built client-side, see ``event_registration_survey.esm.js``)
        rather than as individual form fields, since Odoo's POST param
        binding for ``type="http"`` routes only keeps the first value for a
        repeated field name, which would drop extra selections on
        multiple_choice/matrix questions.

        :param dict post: values posted by the registration form
        :return: a copy of ``post`` with ``post-data`` merged in and removed
        :rtype: dict
        """
        post = dict(post)
        post_data_raw = post.pop("post-data", None)
        if post_data_raw:
            try:
                post.update(json.loads(post_data_raw))
            except json.JSONDecodeError:
                _logger.error("Failed to parse 'post-data' as JSON")
        return post

    @http.route()
    def registration_confirm(self, event, **post):
        """Merge the survey answers, then delegate to core.

        Core handles reCAPTCHA verification, seat availability, attendee
        creation and the sale/checkout redirect. The sorted survey answers
        are stashed on the request so
        :meth:`_create_attendees_from_registration_post` can reuse them
        further down the call chain.

        :param event.event event: event the registration is for
        :param post: values posted by the registration form
        """
        post = self._merge_survey_post_data(post)
        if event.survey_ids:
            request.event_registration_survey_form_details = self._sort_form_details(
                post
            )
        return super().registration_confirm(event, **post)

    def _process_attendees_form(self, event, form_details):
        """Route to the survey-aware parser for events using a survey.

        The posted field names then follow the
        ``{counter}-{question_id}-{survey_id}`` convention instead of core's
        ``{counter}-{question_type}-{question_id}`` one. Core calls this
        method more than once per request (seat availability, then pricing
        in ``website_event_sale``), so the sorted details computed in
        :meth:`registration_confirm` are reused instead of sorting the
        posted data again.

        :param event.event event: event the registration is for
        :param dict form_details: values posted by the registration form
        :return: list of dicts, one per attendee registration
        :rtype: list
        """
        if event.survey_ids:
            sorted_details = getattr(
                request, "event_registration_survey_form_details", None
            ) or self._sort_form_details(form_details)
            return self._process_attendees_form_survey(event, sorted_details)
        return super()._process_attendees_form(event, form_details)

    def _create_attendees_from_registration_post(self, event, registration_data):
        """Create the attendees, then schedule survey processing for each.

        :param event.event event: event the registration is for
        :param list registration_data: list of dicts, one per attendee
            registration
        :return: the created attendees
        :rtype: event.registration
        """
        attendees_sudo = super()._create_attendees_from_registration_post(
            event, registration_data
        )
        form_details = getattr(request, "event_registration_survey_form_details", None)
        if form_details:
            delay_time = timedelta(minutes=1)
            start_time = datetime.now() + delay_time
            for reg, form_detail in zip(  # noqa: B905
                attendees_sudo, form_details.values()
            ):
                reg.with_delay(eta=start_time).process_survey(reg.id, form_detail)
        return attendees_sudo

    # flake8: noqa: C901
    def _process_attendees_form_survey(self, event, form_details):
        """Build the registration values from the sorted survey answers.

        :param event.event event: event the registration is for
        :param dict form_details: return value of :meth:`_sort_form_details`
        :return: list of dicts, one per attendee registration
        :rtype: list
        """
        registrations = {}
        question_ids = set()

        # Fetch all questions in a single query.
        for registration_info in form_details.values():
            for survey_counter, survey_info in registration_info.items():  # noqa: B007
                if isinstance(survey_info, dict):
                    question_ids.update(
                        int(key) for key in survey_info.keys() if key.isdigit()
                    )
        questions = {
            q.id: q for q in request.env["survey.question"].sudo().browse(question_ids)
        }

        for registration_counter, registration_info in form_details.items():
            registrations[registration_counter] = {}

            event_ticket_id = int(registration_info.get("event_ticket_id", False))
            if event_ticket_id == 0:
                event_ticket_id = False
            registrations[registration_counter]["event_ticket_id"] = event_ticket_id

            partner_values = {}
            for survey_info in registration_info.values():
                # "event_ticket_id"/"event_id" sit next to the survey-counter
                # keyed dicts at this level; only the latter hold answers.
                if not isinstance(survey_info, dict):
                    continue

                for key, value in survey_info.items():
                    if not key.isdigit():
                        continue
                    current_question = questions.get(int(key))
                    if not current_question:
                        continue
                    if current_question.save_as_firstname:
                        partner_values["firstname"] = value
                    if current_question.save_as_lastname:
                        partner_values["lastname"] = value
                    if current_question.save_as_email:
                        partner_values["email"] = value
                    if current_question.save_as_phone:
                        partner_values["phone"] = value

            registrations[registration_counter].update(partner_values)

        for registration_counter, registration in registrations.items():  # noqa: B007
            lastname = registration.pop("lastname", "")
            firstname = registration.pop("firstname", "")
            registration["name"] = f"{lastname} {firstname}".strip()

        _logger.debug(
            "Registration values from controller:\n%s", list(registrations.values())
        )

        return list(registrations.values())

    def _sort_form_details(self, form_details):
        """Organize data posted from the attendee details form in a nested dictionary.

        :param dict form_details: posted data from frontend registration form, like::

            {
                'nb_register-0': '1',
                '1-event_ticket_id': '1',
                '1-event_id': '1',
                '1-survey-1': '00877e81-e25d-4ae7-afca-945a95ba1442',
                '1-answer-1': 'f266f206-dc57-4abb-9eea-9c292e70a783',
                'csrf_token': '687ec3ab0aa1cbd4139199030b1af786ffeea88do1656590004',
                '1-1-1': 'Name',
                '1-2-1': 'email@email.com',
                '1-3-1': '0401234567',
                '1-4-1': '2021-06-25',
                '1-5-1': '2021-06-25 19:00:00',
                '1-6-2': ['14', {'comment': ''}],
                '1-7-2': {'18', ['15'], '19': ['15']},
                ...
            }

        :return: a dictionary like::

            {
                '1': {
                    '1': {
                        'survey': '2abe3699-dc2f-428f-b0b8-fcfc8de2816a',
                        'answer': '6cb0e410-3c32-4956-aae1-1c96dc590f1a',
                        '1': 'Name',
                        '2': 'email@email.com',
                        '3': '0401234567',
                        '4': '2021-07-16'
                    }, '2': {
                        'survey': 'df8026d6-beec-4dab-a18f-659f8a374a43',
                        'answer': '2c8f6c6e-3011-4dc7-9381-4a1f1f990f98',
                        '5': '2021-07-23 21:00:03',
                        '6': ['14', {'comment': ''}],
                        '7': {'18': ['15'], '19': ['15']},
                    },
                    'event_ticket_id': '1',
                    'event_id': '1'
                }
            }

        :rtype: dict
        """
        registrations = {}
        for key, value in form_details.items():
            # Only "{counter}-..." fields are ours (see event_templates.xml);
            # anything else - csrf_token, nb_register-*, or a field posted by
            # an unrelated module - is left alone.
            if "-" not in key or key.startswith("nb_register"):
                continue
            registration_counter, attr_name = key.split("-", 1)
            if not registration_counter.isdigit():
                continue
            if registration_counter not in registrations:
                registrations[registration_counter] = {}
            if "-" in attr_name:
                field_name, survey_counter = attr_name.split("-", 1)
                registrations[registration_counter].setdefault(survey_counter, {})[
                    field_name
                ] = value
            else:
                registrations[registration_counter][attr_name] = value
        _logger.debug("Sorted registration details:\n%s", registrations)
        return registrations
