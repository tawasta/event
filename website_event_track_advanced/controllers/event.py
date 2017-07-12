# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http, fields
from odoo.http import request

# 4. Imports from Odoo modules (rarely, and only if necessary):

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in


class WebsiteEvent(http.Controller):
    """
    Controller for handling product quick-purchases
    """

    @http.route(
        ['''/event/<model("event.event", "[('show_track_proposal','=',1)]"):event>/cfp'''],
        type='http',
        auth='public',
        website=True
    )
    def event_track_proposal(self, event, **post):
        return request.render("website_event_call_for_papers.event_call_for_papers", {'event': event})
