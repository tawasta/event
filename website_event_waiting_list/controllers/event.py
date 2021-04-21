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

# 2. Known third party imports:
import werkzeug

# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventControllerWaiting(WebsiteEventController):

    @http.route(['/event/<model("event.event"):event>/registration/new'], type='json', auth="public", methods=['POST'], website=True)
    def registration_new(self, event, **post):
        """
        Registration modal and
        Waiting list modal
        """
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        tickets = self._process_tickets_form(event, post)
        availability_check = True
        waiting_list_check = False
        if event.seats_limited:
            ordered_seats = 0
            for ticket in tickets:
                ordered_seats += ticket['quantity']
            if not event.waiting_list and event.seats_available < ordered_seats:
                availability_check = False
            if event.waiting_list and event.seats_available <= 0:
                waiting_list_check = True
        if not tickets and not waiting_list_check:
            return False
        if waiting_list_check:
            return request.env['ir.ui.view']._render_template("website_event_waiting_list.waiting_list_attendee_details", {'tickets': tickets, 'event': event, 'waiting_list_check': waiting_list_check})
        return request.env['ir.ui.view']._render_template("website_event.registration_attendee_details", {'tickets': tickets, 'event': event, 'availability_check': availability_check, 'waiting_list_check': waiting_list_check})

    @http.route(['''/event/<model("event.event"):event>/registration/confirm'''], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        """
        Return registration confirmation after registering or
        Return waiting list confirmation after joining waiting list
        """
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        registrations = self._process_attendees_form(event, post)
        attendees_sudo = self._create_attendees_from_registration_post(event, registrations)
        for attendee in attendees_sudo:
            if attendee.state == 'wait':
                return request.render("website_event_waiting_list.waiting_list_complete",
                                  self._get_registration_confirm_values(event, attendees_sudo))
        return request.render("website_event.registration_complete",
                                  self._get_registration_confirm_values(event, attendees_sudo))

    @http.route([
        '/event/<model("event.event"):event>/waiting-list/confirm/<model("event.registration"):registration>/<string:code>',
    ],
                type='http', auth="public", website=True)
    def confirm_url_template(self, event, registration, code, **post):
        """
        Return correct confirmation page depending on state
        Confirm state changes on post
        """
        if code == registration.access_token:
            render_values = {
                'event': event,
                'registration': registration,
            }
            if post:
                new_state = post.get("new_state")
                cur_state = post.get("current_state")
                if cur_state == "wait" and new_state == "open" and event.seats_available >= 1:
                    registration.write({'state': 'open'})
                if new_state == "cancel":
                    registration.write({'state': 'cancel'})

            if registration.state in ['wait', 'cancel', 'open']:
                return request.render("website_event_waiting_list.confirm_waiting", render_values)
        return request.render("website.page_404")
