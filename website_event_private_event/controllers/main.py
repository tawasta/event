from odoo import http
from odoo.fields import Domain

from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_event.controllers.main import WebsiteEventController


def sitemap_public_event(env, rule, qs):
    """List only the events that are not private.

    Core generates the sitemap of the event page from every event that is
    visible to the visitor, so a private event would end up in search engines.
    """
    website = env["website"].get_current_website()
    domain = (
        sitemap_qs2dom(qs, "/event", "name")
        & website.website_domain()
        & Domain("is_private_event", "=", False)
    )
    for event in env["event.event"].search(domain):
        yield {"loc": f"/event/{env['ir.http']._slug(event)}"}


class WebsiteEventPrivateEventController(WebsiteEventController):
    @http.route(sitemap=sitemap_public_event)
    def event(self, event, **post):
        return super().event(event, **post)
