from odoo import models
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)


class WebsiteSnippetFilterEventFix(models.Model):
    _inherit = "website.snippet.filter"

    def _get_company_domain(self, model_name, domain):
        if model_name == "event.event":
            return domain
        return super()._get_company_domain(model_name, domain)
