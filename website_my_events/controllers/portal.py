import json
from collections import OrderedDict
from operator import itemgetter

from odoo import _, fields, http
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
            # event.event's own _order is "date_begin, id", so ordering by
            # the bare relation field sorts by the event's date.
            "date": {"label": _("Newest"), "order": "event_id desc"},
            # Sorted in Python (see _sort_registrations_by_event_name):
            # the ORM's order clause can't sort through a relation by a
            # field on the comodel other than via the comodel's own _order,
            # which for event.event/event.event.ticket doesn't start with
            # name.
            "event": {"label": _("Event"), "order": "event_id"},
            "ticket": {"label": _("Ticket"), "order": "event_ticket_id"},
            "state": {"label": _("Status"), "order": "state"},
            "event_status": {"label": _("Event Status"), "order": "event_id"},
        }

    def _get_event_searchbar_groupby(self):
        return {
            "none": {"input": "none", "label": _("None")},
            "event": {"input": "event", "label": _("Event")},
            "ticket": {"input": "ticket", "label": _("Ticket")},
            "state": {"input": "state", "label": _("Status")},
            "event_status": {"input": "event_status", "label": _("Event Status")},
        }

    def _get_event_searchbar_inputs(self):
        return {
            "all": {"input": "all", "label": _("Search in All")},
            "event": {"input": "event", "label": _("Search in Event")},
            "ticket": {"input": "ticket", "label": _("Search in Ticket")},
            "status": {"input": "status", "label": _("Search in Status")},
            "event_status": {
                "input": "event_status",
                "label": _("Search in Event Status"),
            },
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

    def _get_event_state_labels(self):
        return {
            "open": _("Confirmed"),
            "draft": _("Unconfirmed"),
            "done": _("Attended"),
            "cancel": _("Cancelled"),
            "wait": _("Waiting"),
        }

    def _get_event_date_status_labels(self):
        return {
            "upcoming": _("Upcoming"),
            "ongoing": _("Ongoing"),
            "ended": _("Ended"),
        }

    def _get_event_date_status_classes(self):
        return {
            "upcoming": "text-bg-primary",
            "ongoing": "text-bg-success",
            "ended": "text-bg-secondary",
        }

    def _get_event_date_status_order(self):
        return {
            "ongoing": 1,
            "upcoming": 2,
            "ended": 3,
        }

    def _get_event_date_status(self, event):
        now = fields.Datetime.now()

        if event.date_end and event.date_end < now:
            return "ended"

        if event.date_begin and event.date_begin > now:
            return "upcoming"

        return "ongoing"

    def _get_event_status_data(self, registrations):
        labels = self._get_event_date_status_labels()
        classes = self._get_event_date_status_classes()

        event_status_data = {}
        for registration in registrations:
            event = registration.event_id
            if not event:
                continue

            status = self._get_event_date_status(event)
            event_status_data[event.id] = {
                "status": status,
                "label": labels[status],
                "class": classes[status],
            }

        return event_status_data

    def _get_event_status_search_domain(self, search):
        search_lower = search.lower()
        labels = self._get_event_date_status_labels()
        now = fields.Datetime.now()
        domains = []

        for status, label in labels.items():
            if search_lower in label.lower() or search_lower in status:
                if status == "upcoming":
                    domains.append([("event_id.date_begin", ">", now)])
                elif status == "ongoing":
                    domains.append(
                        [
                            ("event_id.date_begin", "<=", now),
                            ("event_id.date_end", ">=", now),
                        ]
                    )
                elif status == "ended":
                    domains.append([("event_id.date_end", "<", now)])

        return OR(domains) if domains else []

    def _get_event_search_domain(self, search_in, search):
        search_domain = []

        if search_in in ("event", "all"):
            search_domain.append([("event_id.name", "ilike", search)])

        if search_in in ("ticket", "all"):
            search_domain.append([("event_ticket_id.name", "ilike", search)])

        if search_in in ("status", "all"):
            search_lower = search.lower()
            matched_states = []

            for state, label in self._get_event_state_labels().items():
                if search_lower in label.lower() or search_lower in state.lower():
                    matched_states.append(state)

            if matched_states:
                search_domain.append([("state", "in", matched_states)])

        if search_in in ("event_status", "all"):
            event_status_domain = self._get_event_status_search_domain(search)
            if event_status_domain:
                search_domain.append(event_status_domain)

        return OR(search_domain) if search_domain else []

    def _sort_registrations_by_event_name(self, registrations):
        return registrations.sorted(
            key=lambda registration: (
                (registration.event_id.name or "").lower(),
                registration.id,
            )
        )

    def _sort_registrations_by_ticket_name(self, registrations):
        return registrations.sorted(
            key=lambda registration: (
                (registration.event_ticket_id.name or "").lower(),
                registration.id,
            )
        )

    def _sort_registrations_by_event_status(self, registrations):
        status_order = self._get_event_date_status_order()
        return registrations.sorted(
            lambda registration: (
                status_order.get(
                    self._get_event_date_status(registration.event_id),
                    99,
                ),
                registration.event_id.date_begin or fields.Datetime.now(),
                registration.create_date,
            )
        )

    def _group_registrations_by_event_status(self, registrations):
        status_order = self._get_event_date_status_order()
        sorted_registrations = registrations.sorted(
            lambda registration: (
                status_order.get(
                    self._get_event_date_status(registration.event_id),
                    99,
                ),
                registration.event_id.date_begin or fields.Datetime.now(),
                registration.create_date,
            )
        )

        grouped_registrations = []
        current_status = False
        current_group = request.env["event.registration"].sudo()

        for registration in sorted_registrations:
            status = self._get_event_date_status(registration.event_id)

            if current_status and status != current_status:
                grouped_registrations.append(current_group)
                current_group = request.env["event.registration"].sudo()

            current_status = status
            current_group |= registration

        if current_group:
            grouped_registrations.append(current_group)

        return grouped_registrations

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

        python_sort_key = "event_status" if groupby == "event_status" else sortby

        if python_sort_key in ("event_status", "event", "ticket"):
            all_registrations = event_obj.sudo().search(domain, order=order)
            if python_sort_key == "event_status":
                all_registrations = self._sort_registrations_by_event_status(
                    all_registrations
                )
            elif python_sort_key == "event":
                all_registrations = self._sort_registrations_by_event_name(
                    all_registrations
                )
            else:
                all_registrations = self._sort_registrations_by_ticket_name(
                    all_registrations
                )
            registrations = all_registrations[
                pager["offset"] : pager["offset"] + self._items_per_page
            ]
        else:
            registrations = event_obj.sudo().search(
                domain,
                order=order,
                limit=self._items_per_page,
                offset=pager["offset"],
            )

        if groupby == "event_status":
            grouped_registrations = self._group_registrations_by_event_status(
                registrations
            )
        else:
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
                "event_status_data": self._get_event_status_data(registrations),
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
