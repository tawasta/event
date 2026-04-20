import logging

from werkzeug.datastructures import OrderedMultiDict

from odoo import _, http
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_event.controllers.main import WebsiteEventController

_logger = logging.getLogger(__name__)

# Use a descriptive but less obvious route for the private event selection page.
# The goal is not security-through-obscurity alone, but to avoid exposing an
# unnecessarily obvious /private-event endpoint.
PRIVATE_EVENT_ROUTE = "/invited-registration/event-selection"


class WebsiteEventPrivateController(WebsiteEventController):
    def _redirect_private_user_to_login(self):
        """Redirect anonymous visitors to login while preserving the current URL.

        This is used for private event endpoints that must only be available to
        authenticated users. After login, Odoo redirects the user back to the
        original target URL.
        """
        redirect_url = request.httprequest.full_path or request.httprequest.path
        if redirect_url.endswith("?"):
            redirect_url = redirect_url[:-1]
        return request.redirect("/web/login?redirect=%s" % redirect_url)

    def _ensure_private_event_access(self, event):
        """Allow normal public events to behave as in core, but block anonymous
        access to private events.

        The private listing itself is already protected with auth="user", but
        direct access to event detail, menu pages, register endpoints and
        registration flows must also be guarded in case someone knows the URL.
        """
        if event.is_private_event and request.env.user._is_public():
            return self._redirect_private_user_to_login()
        return False

    def _apply_private_headers(self, response):
        """Apply SEO and caching protection headers for private pages.

        X-Robots-Tag discourages indexing, while the cache headers reduce the
        chance of private pages being stored by browsers or intermediary caches.
        """
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        response.headers[
            "Cache-Control"
        ] = "private, no-store, no-cache, max-age=0, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @http.route(
        [
            PRIVATE_EVENT_ROUTE,
            PRIVATE_EVENT_ROUTE + "/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
        sitemap=False,
    )
    def private_events(self, page=1, **searches):
        """Render a dedicated website event listing that only exposes private events.

        This route intentionally reuses the standard website_event listing flow so that
        the frontend behavior, filters, pager and template output stay aligned with the
        core module. The main difference is that a custom context flag is injected
        (`private_event_listing=True`), allowing the model layer to adapt the event
        search domain and return only records marked as private.

        The route is excluded from the sitemap and the response is marked with
        noindex and no-cache semantics because this listing must not be publicly
        discoverable or cached aggressively.
        """
        Event = request.env["event.event"].with_context(private_event_listing=True)
        SudoEventType = request.env["event.type"].sudo()

        searches.setdefault("search", "")
        searches.setdefault("date", "upcoming")
        searches.setdefault("tags", "")
        searches.setdefault("type", "all")
        searches.setdefault("country", "all")

        website = request.website.with_context(private_event_listing=True)

        step = 12

        options = self._get_events_search_options(**searches)
        order = "date_begin"
        if searches.get("date", "upcoming") == "old":
            order = "date_begin desc"
        order = "is_published desc, " + order + ", id desc"

        search = searches.get("search")

        event_count, details, fuzzy_search_term = website._search_with_fuzzy(
            "events",
            search,
            limit=page * step,
            order=order,
            options=options,
        )

        event_details = details[0]
        events = event_details.get("results", Event)
        events = events[(page - 1) * step : page * step]

        domain_search = (
            [("name", "ilike", fuzzy_search_term or searches["search"])]
            if searches["search"]
            else []
        )

        no_date_domain = event_details["no_date_domain"]
        dates = event_details["dates"]

        for date in dates:
            if date[0] not in ["all", "old"]:
                date_domain = expression.AND(no_date_domain) + domain_search + date[2]
                date[3] = Event.search_count(date_domain)

        no_country_domain = event_details["no_country_domain"]

        countries = Event.read_group(
            expression.AND(no_country_domain) + domain_search,
            ["id", "country_id"],
            groupby="country_id",
            orderby="country_id",
        )
        countries.insert(
            0,
            {
                "country_id_count": sum(
                    int(country["country_id_count"]) for country in countries
                ),
                "country_id": ("all", _("All Countries")),
            },
        )

        search_tags = event_details["search_tags"]
        current_date = event_details["current_date"]
        current_type = None
        current_country = None

        if searches["type"] != "all":
            current_type = SudoEventType.browse(int(searches["type"]))

        if searches["country"] != "all" and searches["country"] != "online":
            current_country = request.env["res.country"].browse(
                int(searches["country"])
            )

        pager = website.pager(
            url=PRIVATE_EVENT_ROUTE,
            url_args=searches,
            total=event_count,
            page=page,
            step=step,
            scope=5,
        )

        keep = QueryURL(
            PRIVATE_EVENT_ROUTE,
            **{
                key: value
                for key, value in searches.items()
                if (
                    key == "search"
                    or (value != "upcoming" if key == "date" else value != "all")
                )
            },
        )

        searches["search"] = fuzzy_search_term or search

        values = {
            "current_date": current_date,
            "current_country": current_country,
            "current_type": current_type,
            "event_ids": events,
            "dates": dates,
            "categories": request.env["event.tag.category"].search(
                [
                    ("is_published", "=", True),
                    "|",
                    ("website_id", "=", website.id),
                    ("website_id", "=", False),
                ]
            ),
            "countries": countries,
            "pager": pager,
            "searches": searches,
            "search_tags": search_tags,
            "keep": keep,
            "search_count": event_count,
            "original_search": fuzzy_search_term and search,
            "website": website,
            # This flag is consumed by the inherited website layout template to
            # inject a robots meta tag into the HTML head.
            "private_event_noindex": True,
        }

        if searches["date"] == "old":
            values["canonical_params"] = OrderedMultiDict([("date", "old")])

        response = request.render("website_event.index", values)
        return self._apply_private_headers(response)

    @http.route(
        ["""/event/<model("event.event"):event>"""],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def event(self, event, **post):
        """Extend the core event redirect endpoint without replacing its behavior.

        For public events, core behavior is preserved. For private events, access
        is restricted to authenticated users before delegating to the standard
        redirect logic.
        """
        private_redirect = self._ensure_private_event_access(event)
        if private_redirect:
            return private_redirect

        response = super().event(event, **post)

        if event.is_private_event:
            return self._apply_private_headers(response)

        return response

    @http.route(
        ["""/event/<model("event.event"):event>/page/<path:page>"""],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def event_page(self, event, page, **post):
        """Protect custom event menu pages for private events.

        Event subpages can expose content even when the main listing is private,
        so the same access control must be applied here as well.
        """
        private_redirect = self._ensure_private_event_access(event)
        if private_redirect:
            return private_redirect

        response = super().event_page(event, page, **post)

        if event.is_private_event:
            return self._apply_private_headers(response)

        return response

    def _prepare_event_register_values(self, event, **post):
        """Inject private-event SEO flags into the registration page values.

        The core controller prepares the qcontext used by
        `website_event.event_description_full`. This override keeps the default
        preparation logic and only enriches the rendering values for private
        events so that the inherited website layout can inject a robots meta tag
        into the final HTML page.
        """
        values = super()._prepare_event_register_values(event, **post)

        if event.is_private_event:
            values["private_event_noindex"] = True

        return values

    @http.route(
        ["""/event/<model("event.event"):event>/register"""],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def event_register(self, event, **post):
        """Extend the standard event registration page response for private events.

        The core route rendering is preserved, but private events require login
        and receive additional privacy headers.
        """
        private_redirect = self._ensure_private_event_access(event)
        if private_redirect:
            return private_redirect

        response = super().event_register(event, **post)

        if event.is_private_event:
            return self._apply_private_headers(response)

        return response
