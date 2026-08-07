##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
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
# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.website_event.controllers.main import WebsiteEventController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistrationPrivacy(WebsiteEventController):
    def _extract_privacy_vals(self, post):
        """Pull the posted ``privacy_<activity_id>`` checkbox values out of ``post``.

        :param dict post: values posted by the registration form
        :return: mapping of ``privacy_<activity_id>`` field name to its
            posted value, for every such field present
        :rtype: dict
        """
        return {key: value for key, value in post.items() if key.startswith("privacy_")}

    @http.route()
    def registration_confirm(self, event, **post):
        """Stash the posted privacy consents, then delegate to core.

        Recorded only once :meth:`_create_attendees_from_registration_post`
        has resolved each attendee's ``partner_id``, since core may still
        change it before then.

        :param event.event event: event the registration is for
        :param post: values posted by the registration form
        """
        request.event_privacy_form_vals = self._extract_privacy_vals(post)
        return super().registration_confirm(event, **post)

    def _create_attendees_from_registration_post(self, event, registration_data):
        """Record each attendee's privacy consents after core creates them.

        Only relies on the ``partner_id`` core already sets on each
        attendee, so it works regardless of how they were produced.
        Skips attendees with no resolved partner.

        :param event.event event: event the registration is for
        :param list registration_data: list of dicts, one per attendee
            registration
        :return: the created attendees
        :rtype: event.registration
        """
        attendees_sudo = super()._create_attendees_from_registration_post(
            event, registration_data
        )
        if event.privacy_ids:
            privacy_vals = getattr(request, "event_privacy_form_vals", {})
            for attendee in attendees_sudo:
                if attendee.partner_id:
                    request.env["event.registration"]._create_privacy(
                        privacy_vals, attendee.partner_id, event
                    )
        return attendees_sudo
