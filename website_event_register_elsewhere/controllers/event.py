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
from odoo import http
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventControllerElsewhere(WebsiteEventController):
    """Keep the registration out of Odoo when it is made on another website.

    The page has no register button then, but the routes of the registration
    can still be called directly, so they are closed here too.
    """

    @http.route()
    def registration_new(self, event, **post):
        if event.registration_elsewhere:
            return False
        return super().registration_new(event, **post)

    @http.route()
    def registration_confirm(self, event, **post):
        if event.registration_elsewhere:
            # local=False: the link is outside this site, and checked when saved
            return request.redirect(event.registration_link, local=False)
        return super().registration_confirm(event, **post)
