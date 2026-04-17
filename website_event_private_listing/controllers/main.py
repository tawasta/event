import logging

from werkzeug.datastructures import OrderedMultiDict

from odoo import _, http
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_event.controllers.main import WebsiteEventController

_logger = logging.getLogger(__name__)


class WebsiteEventPrivateController(WebsiteEventController):
    @http.route(
        [
            "/private-event",
            "/private-event/page/<int:page>",
            "/private-events",
            "/private-events/page/<int:page>",
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
        X-Robots-Tag / noindex semantics because this listing must not be promoted
        to external search engines.
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
                    [int(country["country_id_count"]) for country in countries]
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
            url="/private-event",
            url_args=searches,
            total=event_count,
            page=page,
            step=step,
            scope=5,
        )

        keep = QueryURL(
            "/private-event",
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
            "private_event_noindex": True,
        }

        if searches["date"] == "old":
            values["canonical_params"] = OrderedMultiDict([("date", "old")])

        response = request.render("website_event.index", values)
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

    @http.route(
        ["""/event/<model("event.event"):event>"""],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def event(self, event, **post):
        """Extend the core event redirect endpoint without replacing its behavior.

        In website_event, this route redirects the visitor either to the first
        event menu page or to the registration page. Here the method intentionally
        delegates the standard routing logic to `super()` and only appends SEO
        protection headers when the target event is marked as private.

        This keeps the core navigation flow untouched while ensuring that private
        event entry URLs are discouraged from being indexed.
        """
        response = super().event(event, **post)

        if event.is_private_event:
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"

        return response

    def _prepare_event_register_values(self, event, **post):
        """Inject private-event SEO flags into the registration page values.

        The core controller prepares the qcontext used by
        `website_event.event_description_full`. This override keeps the default
        preparation logic and only enriches the rendering values for private
        events so that the inherited website layout can inject a robots meta tag
        into the final HTML page.

        Using this helper override is the most Odoo-friendly approach because the
        extra value is added at qcontext preparation time, instead of duplicating
        the whole registration controller rendering logic.
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

        The core website_event route already renders the registration page and is
        not included in the sitemap. This override keeps that rendering logic via
        `super()` and adds an X-Robots-Tag header when the event is private.

        Combined with `_prepare_event_register_values()`, this ensures that the
        private registration page is protected both at HTTP header level and at
        HTML meta level.
        """
        response = super().event_register(event, **post)
        if event.is_private_event:
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"

        return response
