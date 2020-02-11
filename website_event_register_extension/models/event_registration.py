# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventRegistration(models.Model):

    # 1. Private attributes
    _inherit = 'event.registration'

    # Add ticket to free events
    def _prepare_registration(self, event, post, user_id, partner=False):

        res = dict()
        res = super(EventRegistration, self)\
            ._prepare_registration(event, post, user_id, partner=partner)
        ticket = self.env['event.event.ticket']\
            .search([('event_id', '=', event.id), ('price', '=', '0')]).id
        res['event_ticket_id'] = ticket
        return res
