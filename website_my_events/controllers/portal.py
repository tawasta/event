import json
from collections import OrderedDict
from operator import itemgetter

from odoo import _, http
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class PortalEvent(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "event_count" in counters:
            event_model = request.env["event.registration"]
            event_count = (
                event_model.search_count([])
                if event_model.check_access_rights("read", raise_exception=False)
                else 0
            )
            values["event_count"] = event_count
        return values

    def _get_event_searchbar_sortings(self):
        return {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "event": {"label": _("Event"), "order": "event_id"},
            "ticket": {"label": _("Ticket"), "order": "event_ticket_id"},
            "state": {"label": _("Status"), "order": "state"},
        }

    def _get_event_searchbar_groupby(self):
        return {
            "none": {"input": "none", "label": _("None")},
            "event": {"input": "event", "label": _("Event")},
            "ticket": {"input": "ticket", "label": _("Ticket")},
            "state": {"input": "state", "label": _("Status")},
        }

    def _get_event_searchbar_inputs(self):
        return {
            "all": {"input": "all", "label": _("Search in All")},
            "event": {"input": "event", "label": _("Search in Event")},
            "ticket": {"input": "ticket", "label": _("Search in Ticket")},
            "status": {"input": "status", "label": _("Search in Status")},
        }

    def _get_event_groupby_mapping(self):
        return {
            "event": "event_id",
            "ticket": "event_ticket_id",
            "state": "state",
        }

    def _get_event_order(self, order, groupby):
        group = self._get_event_groupby_mapping().get(groupby)
        return f"{group}, {order}" if group else order

    def _get_event_search_domain(self, search_in, search):
        search_domain = []

        if search_in in ("event", "all"):
            search_domain.append([("event_id.name", "ilike", search)])

        if search_in in ("ticket", "all"):
            search_domain.append([("event_ticket_id.name", "ilike", search)])

        if search_in in ("status", "all"):
            search_domain.append([("state", "ilike", search)])

        return OR(search_domain)

    @http.route(
        ["/my/events", "/my/events/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_events(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        groupby=None,
        search=None,
        search_in="all",
        **kw,
    ):
        values = self._prepare_portal_layout_values()
        event_obj = request.env["event.registration"]

        # Avoid error if the user does not have access.
        if not event_obj.check_access_rights("read", raise_exception=False):
            return request.redirect("/my")

        domain = [
            ("partner_id", "=", request.env.user.partner_id.id),
            ("state", "!=", "draft"),
        ]

        searchbar_sortings = self._get_event_searchbar_sortings()
        searchbar_groupby = self._get_event_searchbar_groupby()
        searchbar_inputs = self._get_event_searchbar_inputs()

        if not sortby or sortby not in searchbar_sortings:
            sortby = "date"

        if not groupby or groupby not in searchbar_groupby:
            groupby = "none"

        if not search_in or search_in not in searchbar_inputs:
            search_in = "all"

        order = self._get_event_order(searchbar_sortings[sortby]["order"], groupby)

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        if search:
            domain += self._get_event_search_domain(search_in, search)

        registration_count = event_obj.sudo().search_count(domain)

        pager = portal_pager(
            url="/my/events",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "groupby": groupby,
                "search": search,
                "search_in": search_in,
            },
            total=registration_count,
            page=page,
            step=self._items_per_page,
        )

        registrations = event_obj.sudo().search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        )

        group = self._get_event_groupby_mapping().get(groupby)
        if group:
            grouped_registrations = [
                event_obj.sudo().concat(*g)
                for _k, g in groupbyelem(registrations, itemgetter(group))
            ]
        else:
            grouped_registrations = [registrations] if registrations else []

        values.update(
            {
                "registrations": registrations,
                "grouped_registrations": grouped_registrations,
                "page_name": "Events",
                "default_url": "/my/events",
                "pager": pager,
                "date": date_begin,
                "date_end": date_end,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_groupby": OrderedDict(sorted(searchbar_groupby.items())),
                "searchbar_inputs": OrderedDict(sorted(searchbar_inputs.items())),
                "sortby": sortby,
                "groupby": groupby,
                "search": search,
                "search_in": search_in,
            }
        )
        return request.render("website_my_events.portal_my_events", values)

    @http.route(
        ["/registration/cancel/<int:registration_id>"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def cancel_registration(self, registration_id=None, **post):
        registration = (
            request.env["event.registration"]
            .sudo()
            .search([("id", "=", registration_id)])
        )
        registration.sudo().action_cancel()
        values = {}
        return json.dumps(values)
