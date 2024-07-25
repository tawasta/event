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
import logging

# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController

# 4. Imports from Odoo modules:
from odoo.addons.website_event_waiting_list.controllers.event import (
    WebsiteEventControllerWaiting,
)

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class WebsiteEventSaleWaitingListController(
    WebsiteEventSaleController, WebsiteEventControllerWaiting
):
    @http.route(
        ['/event/<model("event.event"):event>/registration/manage/<string:code>'],
        type="http",
        auth="public",
        website=True,
    )
    def confirm_url_template(self, event, code, **post):
        """
        Return correct confirmation page depending on state
        Confirm state changes on post
        """
        for registration in event.sudo().registration_ids:
            logging.info(registration.event_id)
            if registration.sudo().access_token == code:
                render_values = {
                    "event": event,
                    "registration": registration,
                    "ticket": registration.event_ticket_id,
                }
                if post:
                    logging.info("==POST===")
                    new_state = post.get("new_state")
                    cur_state = post.get("current_state")
                    if (
                        cur_state == "wait"
                        and new_state == "open"
                        and event.sudo().seats_available >= 1
                    ):
                        logging.info("====THIS====")
                        if self._confirm_registration_from_waiting_list(registration):
                            registration.sudo().write(
                                {"confirmed_from_waiting_list": True}
                            )
                            logging.info("===THIS1====")
                            logging.info(registration.sale_order_id)
                            logging.info(registration.sale_order_line_id)
                            return request.redirect("/shop/checkout")
                        else:
                            logging.info("===OR=====")
                            if registration.event_id.auto_confirm:
                                registration.sudo().write({"state": "open"})
                            else:
                                registration.sudo().write({"state": "draft"})

                    if new_state == "cancel":
                        registration.sudo().action_cancel()

                if registration.sudo().state in ["wait", "cancel", "open"]:
                    return request.render(
                        "website_event_waiting_list.confirm_waiting", render_values
                    )
        return request.render("website.page_404")

    def _confirm_registration_from_waiting_list(self, registration):
        if registration.event_ticket_id:
            order_sudo = request.website.sale_get_order(force_create=True)
            if order_sudo.state != "draft":
                request.website.sale_reset()
                order_sudo = request.website.sale_get_order(force_create=True)

            cart_values = order_sudo._cart_update(
                product_id=registration.event_ticket_id.product_id.id,
                add_qty=1,
                event_ticket_id=registration.event_ticket_id.id,
            )

            registration.sudo().write(
                {
                    "sale_order_id": order_sudo.id,
                    "sale_order_line_id": cart_values.get("line_id"),
                }
            )
            if order_sudo.amount_total:
                return True
            elif order_sudo:
                order_sudo.action_confirm()  # tde notsure: email sending ?
                request.website.sale_reset()
                return False
