# -*- coding: utf-8 -*-

# 1. Standard library imports:
import logging

# 2. Known third party imports:

# 3. Odoo imports:
from odoo.http import request

# 4. Imports from Odoo modules:
from odoo.addons.website_event_track_advanced.controllers.\
    event_track_proposal import WebsiteEventTrackController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:
_logger = logging.getLogger(__name__)


class WebsiteEventTrackController(WebsiteEventTrackController):

    def _get_event_track_proposal_post_values(self, event, **post):
        values = super(WebsiteEventTrackController, self).\
            _get_event_track_proposal_post_values(event, **post)

        if post.get('organizer_business_id') \
                and post.get('organizer_business_id') != 'false':
            values['workshop_organizer']['business_id'] = \
                post.get('organizer_business_id')

        if post.get('organizer_edicode') and \
                post.get('organizer_edicode') != 'false':
            values['workshop_organizer']['edicode'] = \
                post.get('organizer_edicode')

        if post.get('organizer_einvoice_operator') and \
                post.get('organizer_einvoice_operator') != 'false':
            einvoice_operator_module = \
                request.env['res.partner.operator.einvoice']
            operator_name = post.get('organizer_einvoice_operator')

            existing_operator = einvoice_operator_module.sudo().search([
                ('name', 'ilike', operator_name)
            ], limit=1)

            # Create an einvoice operator if one doesn't exist
            if not existing_operator:
                operator_identifier = False
                if post.get('organizer_einvoice_operator_identifier') and \
                        post.get('organizer_einvoice_operator_identifier') \
                        != 'false':
                    operator_identifier = \
                        post.get('organizer_einvoice_operator_identifier')

                existing_operator = einvoice_operator_module.sudo().create(
                    {
                        'name': operator_name,
                        'identifier': operator_identifier})

            values['workshop_organizer']['einvoice_operator'] = \
                existing_operator.id

        return values
