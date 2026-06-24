from odoo import models


class EventEvent(models.Model):
    _inherit = "event.event"

    def _search_get_detail(self, website, order, options):
        detail = super()._search_get_detail(website, order, options)

        search_fields = detail.get("search_fields", [])

        if "description" not in search_fields:
            search_fields.append("description")

        detail["search_fields"] = search_fields

        return detail