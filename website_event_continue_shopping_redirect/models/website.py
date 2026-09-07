##############################################################################
#
#    Author: Futural Oy
#    Copyright 2026 Futural Oy (https://futural.fi)
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

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _get_checkout_step_list(self):
        """
        Point the cart's "Continue shopping" button to /event instead of
        /shop, when the website has no sellable products other than event
        tickets - going "back to shop" would otherwise land on an empty
        product list.
        """
        steps = super()._get_checkout_step_list()
        if self._has_only_event_products_for_sale():
            for xmlids, step in steps:
                if "website_sale.cart" in xmlids:
                    step["back_button_href"] = "/event"
        return steps

    def _has_only_event_products_for_sale(self):
        """Is every sellable, published product on this website an event ticket?"""
        self.ensure_one()
        non_event_products = (
            self.env["product.template"]
            .sudo()
            .with_context(website_id=self.id)
            .search_count(
                [
                    ("sale_ok", "=", True),
                    ("website_published", "=", True),
                    ("detailed_type", "!=", "event"),
                ]
            )
        )
        return not non_event_products
