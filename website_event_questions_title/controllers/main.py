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

# 2. Known third party imports:

# 3. Odoo imports (openerp):

# 4. Imports from Odoo modules:
from odoo.addons.website_event.controllers.main import (
    WebsiteEventController,
)

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventControllerTitle(WebsiteEventController):
    def _process_attendees_form(self, event, form_details):
        registrations = super(
            WebsiteEventControllerTitle, self
        )._process_attendees_form(event, form_details)
        for registration in registrations:
            registration["title"] = []

        for key, value in form_details.items():
            if "title" in key and value:
                registration_index, _question = key.split("-")
                registrations[int(registration_index) - 1]["title"] = value

        return registrations
