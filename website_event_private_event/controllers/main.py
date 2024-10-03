##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:

# 2. Known third party imports:


# 3. Odoo imports (openerp):
from werkzeug.datastructures import OrderedMultiDict

from odoo import _, fields, http
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website.controllers.main import QueryURL

# 4. Imports from Odoo modules:
from odoo.addons.website_event.controllers.main import WebsiteEventController

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventControllerPrivateEvent(WebsiteEventController):
    def sitemap_event(self, rule, qs):
        if not qs or qs.lower() in "/events":
            yield {"loc": "/events"}

    # ------------------------------------------------------------
    # EVENT LIST
    # ------------------------------------------------------------

    def _get_events_search_options(self, **post):
        return {
            "displayDescription": False,
            "displayDetail": False,
            "displayExtraDetail": False,
            "displayExtraLink": False,
            "displayImage": False,
            "allowFuzzy": not post.get("noFuzzy"),
            "date": post.get("date"),
            "tags": post.get("tags"),
            "type": post.get("type"),
            "country": post.get("country"),
        }

    @http.route(
        ["/event", "/event/page/<int:page>", "/events", "/events/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
        sitemap=sitemap_event,
    )
    def events(self, page=1, **searches):
        Event = request.env["event.event"]
        SudoEventType = request.env["event.type"].sudo()

        searches.setdefault("search", "")
        searches.setdefault("date", "upcoming")
        searches.setdefault("tags", "")
        searches.setdefault("type", "all")
        searches.setdefault("country", "all")

        website = request.website

        step = 12  # Number of events per page

        options = self._get_events_search_options(**searches)

        order = "date_begin"
        if searches.get("date", "upcoming") == "old":
            order = "date_begin desc"
        order = "is_published desc, " + order
        search = searches.get("search")

        event_count, details, fuzzy_search_term = website._search_with_fuzzy(
            "events", search, limit=page * step, order=order, options=options
        )
        event_details = details[0]

        events = event_details.get("results", Event)
        events = [event for event in events if not event.is_private_event]
        events = events[(page - 1) * step : page * step]

        # count by domains without self search
        domain_search = (
            [("name", "ilike", fuzzy_search_term or searches["search"])]
            if searches["search"]
            else []
        )

        no_date_domain = event_details["no_date_domain"]
        dates = event_details["dates"]
        for date in dates:
            if date[0] not in ["all", "old"]:
                date[3] = Event.search_count(
                    expression.AND(no_date_domain) + domain_search + date[2]
                )

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
            url="/event",
            url_args=searches,
            total=event_count,
            page=page,
            step=step,
            scope=5,
        )

        keep = QueryURL(
            "/event",
            **{
                key: value
                for key, value in searches.items()
                if (
                    key == "search"
                    or (value != "upcoming" if key == "date" else value != "all")
                )
            }
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
        }

        if searches["date"] == "old":
            # the only way to display this content is to set date=old so it must be canonical
            values["canonical_params"] = OrderedMultiDict([("date", "old")])

        return request.render("website_event.index", values)

    @http.route(
        "/event/get_country_event_list", type="json", auth="public", website=True
    )
    def get_country_events(self, **post):
        Event = request.env["event.event"]
        country_code = request.session["geoip"].get("country_code")
        result = {"events": [], "country": False}
        events = None
        domain = request.website.website_domain()
        if country_code:
            country = request.env["res.country"].search(
                [("code", "=", country_code)], limit=1
            )
            events = Event.search(
                domain
                + [
                    "|",
                    ("address_id", "=", None),
                    ("country_id.code", "=", country_code),
                    ("date_begin", ">=", "%s 00:00:00" % fields.Date.today()),
                    ("is_private_event", "=", False),
                ],
                order="date_begin",
            )
        if not events:
            events = Event.search(
                domain
                + [
                    ("date_begin", ">=", "%s 00:00:00" % fields.Date.today()),
                    ("is_private_event", "=", False),
                ],
                order="date_begin",
            )
        for event in events:
            if country_code and event.country_id.code == country_code:
                result["country"] = country
            result["events"].append(
                {
                    "date": self.get_formated_date(event),
                    "event": event,
                    "url": event.website_url,
                }
            )
        return request.env["ir.ui.view"]._render_template(
            "website_event.country_events_list", result
        )
