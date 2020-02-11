##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2018- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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

# 3. Odoo imports:
from odoo import http, _
from odoo.http import request

# 4. Imports from Odoo modules (rarely, and only if necessary):

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in


class WebsiteEventRegistrationController(http.Controller):

    def _registration_consent_process(self, post):
        """
        Process consent values. This function is inherited and
        modified to process values and return the saved values
        back to route.
        :return dict
        """
        res = dict()
        res['consent_filled'] = True
        return res

    @http.route(
        ['/event/registration/<string:token>'],
        type='http',
        auth="public",
        website=True
    )
    def registration_consent(self, token=None, **post):
        """
        Attendee's are redirected here through link in registration email.
        Capture token, validate it and show template accordingly
        """
        registration = request.env['event.registration'].sudo().search([
            ('token', '=', token)
        ], limit=1)
        values = dict()
        if not registration:
            return request.render("website.403")
        if registration.consent_filled:
            # Redirect to ticket download, since form filled already
            return request.redirect('/event/registration/%s/ticket' % token)
        if post:
            values.update(self._registration_consent_process(post))
            registration.write(values)
            return request.redirect('/event/registration/%s/ticket' % token)
        return request.render(
            'website_event_registration_consent.registration_consent')

    @http.route(
        ['/event/registration/<string:token>/ticket'],
        type='http',
        auth="public",
        website=True
    )
    def registration_ticket(self, token=None, **post):
        """
        Attendee's can download ticket, if form filled and valid token.
        """
        registration = request.env['event.registration'].sudo().search([
            ('token', '=', token)
        ], limit=1)
        if not registration:
            return request.render("website.403")
        if not registration.consent_filled:
            # Redirect to form, since it hasn't been filled yet
            return request.redirect('/event/registration/%s' % token)
        values = {
            'ticket_url': '/event/registration/%s/ticket/download' % token,
            'name': registration.event_id.name,
        }
        return request.render(
            'website_event_registration_consent.registration_consent_thanks',
            values
        )

    @http.route(
        ['/event/registration/<string:token>/ticket/download'],
        type='http',
        auth="public",
        website=True
    )
    def registration_ticket_download(self, token=None, **post):
        """
        Print user's ticket as PDF file
        """
        registration = request.env['event.registration'].sudo().search([
            ('token', '=', token)
        ], limit=1)
        if not registration:
            request.render("website.403")
        report_name = 'website_event_registration_consent.\
            event_registration_ticket_template'
        pdf = request.env['report'].sudo().get_pdf(
            [registration.id],
            report_name,
            data={}
        )
        filename = _('%s_ticket') % registration.name.replace(' ', '_')
        file_headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename="%s.pdf"' % filename)
        ]
        return request.make_response(pdf, headers=file_headers)
