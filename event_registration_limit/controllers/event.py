# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController
import logging

class CustomWebsiteEventRegistrationController(WebsiteEventController):
    @http.route()
    def event_register(self, event, **post):
        partner_id = request.env.user.partner_id.id if request.env.user else None
        registration_disabled = False
        error_message = ""
        
        if partner_id:
            # Tarkistetaan, onko käyttäjällä jo ilmoittautuminen samaan koetyyppiin
            existing_registration = request.env['event.registration'].sudo().search([
                ('registration_survey_id', 'in', event.sudo().survey_ids.ids),
                ('partner_id', '=', partner_id),
                ('state', 'in', ['draft', 'open'])
            ])
            
            if existing_registration:
                registration_disabled = True
                error_message = "Olet jo ilmoittautunut tähän koetyyppiin. Odota arviointia ennen uutta ilmoittautumista."
        
        values = super(CustomWebsiteEventRegistrationController, self).event_register(event, **post)
        values.qcontext.update({
            'registration_disabled': registration_disabled,
            'error_message': error_message
        })
        return values
