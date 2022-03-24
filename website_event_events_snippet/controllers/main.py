##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
import babel.dates

# 3. Odoo imports (openerp):
from odoo import fields, http
from odoo.http import request
from odoo.osv import expression
from odoo.tools.misc import get_lang

# 4. Imports from Odoo modules:
from odoo.addons.website_event.controllers.main import WebsiteEventController

# 2. Known third party imports:


# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventEventsList(WebsiteEventController):
    def get_formated_date(self, event):
        start_date = fields.Datetime.from_string(event.date_begin).date()
        end_date = fields.Datetime.from_string(event.date_end).date()
        month = babel.dates.get_month_names(
            "abbreviated", locale=get_lang(event.env).code
        )[start_date.month]
        return ("%s %s%s") % (
            month,
            start_date.strftime("%e"),
            (end_date != start_date and ("-" + end_date.strftime("%e")) or ""),
        )

    @http.route(["/event/render_events_list"], type="json", auth="public", website=True)
    def render_events_list(self, template, domain, limit=None, order="date_begin asc"):
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        dom = expression.AND(
            [
                [
                    ("website_published", "=", True),
                    ("date_begin", ">=", fields.Datetime.now()),
                ],
                request.website.website_domain(),
            ]
        )
        if domain:
            dom = expression.AND([dom, domain])
        print(dom)
        print(limit)
        print(order)
        events = request.env["event.event"].search(dom, limit=limit, order=order)
        # for event in events:
        #     result["events"].append({"date": self.get_formated_date(event)})
        print(events)
        return request.website.viewref(template)._render(
            {"events": events, "get_formated_date": self.get_formated_date}
        )
