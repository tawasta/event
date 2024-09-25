from odoo import http
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventControllerMaintenance(WebsiteEventController):
    @http.route()
    def events(self, page=1, **searches):
        render_values = {"company": request.website.company_id}
        if request.website._maintenance_mode():
            return request.render(
                "website_sale_maintenance_mode.website_sale_template", render_values
            )
        else:
            response = super().events(page=page, **searches)

            return response

    @http.route()
    def event_page(self, event, page, **post):
        render_values = {"company": request.website.company_id}
        if request.website._maintenance_mode():
            return request.render(
                "website_sale_maintenance_mode.website_sale_template", render_values
            )
        else:
            response = super().event_page(event=event, page=page, **post)

            return response

    @http.route()
    def event(self, event, **post):
        render_values = {"company": request.website.company_id}
        if request.website._maintenance_mode():
            return request.render(
                "website_sale_maintenance_mode.website_sale_template", render_values
            )
        else:
            response = super().event(event=event, **post)

            return response

    @http.route()
    def event_register(self, event, **post):
        render_values = {"company": request.website.company_id}
        if request.website._maintenance_mode():
            return request.render(
                "website_sale_maintenance_mode.website_sale_template", render_values
            )
        else:
            response = super().event_register(event=event, **post)

            return response
