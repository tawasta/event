# 1. Standard library imports:
import logging

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

# 2. Known third party imports:
# 3. Odoo imports (openerp):
# 4. Imports from Odoo modules:

_logger = logging.getLogger(__name__)


class PortalEventTag(CustomerPortal):
    OPTIONAL_BILLING_FIELDS = [
        "zipcode",
        "state_id",
        "vat",
        "company_name",
        "tag_ids",
    ]

    @http.route()
    def account(self, redirect=None, **post):
        if post:
            post.pop("tag_id", None)

            if post.get("tag_ids"):
                tag_ids = list(map(int, post.pop("tag_ids").split(",")))
                request.env.user.partner_id.event_interest_tags = [(6, 0, tag_ids)]
                post.pop("tag_ids", None)
        # Kutsutaan alkuperäisen ohjaimen metodia
        response = super(PortalEventTag, self).account(redirect, **post)

        return response

    def details_form_validate(self, data):
        error, error_message = super(PortalEventTag, self).details_form_validate(data)

        # Allow category_ids to be empty
        if "tag_ids" in data and not data["tag_ids"]:
            data.pop("tag_ids")
            request.env.user.partner_id.event_interest_tags = False

        return error, error_message
