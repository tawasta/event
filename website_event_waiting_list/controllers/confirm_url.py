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
from werkzeug.exceptions import NotFound

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo.http import Controller, request, route, content_disposition

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WaitingConfirmController(Controller):
    @route(['/event/<model("event.event"):event>/confirm/<model("event.registration"):registration>'],
           type='http', auth="public")
    def confirm_url_template(self, event, registration, **kwargs):

        seats_available = event.seats_available
        render_values = {
            'event': event,
            'registration': registration,
            'seats_available': seats_available,
        }
        return request.render("website_event_waiting_list.confirm_waiting", render_values)
