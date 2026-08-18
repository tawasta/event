from odoo import models

from ..const import WORDING_REPLACEMENTS


class Website(models.Model):
    _inherit = "website"

    def get_suggested_controllers(self):
        suggested_controllers = super().get_suggested_controllers()
        return [
            (WORDING_REPLACEMENTS.get(label, label), url, module)
            for label, url, module in suggested_controllers
        ]

    def get_cta_data(self, website_purpose, website_type):
        cta_data = super().get_cta_data(website_purpose, website_type)
        if cta_data and cta_data.get("cta_btn_text"):
            cta_data["cta_btn_text"] = WORDING_REPLACEMENTS.get(
                cta_data["cta_btn_text"], cta_data["cta_btn_text"]
            )
        return cta_data
