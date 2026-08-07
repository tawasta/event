.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Website Event Sale Waiting List
===============================
* Bridges ``website_event_waiting_list`` to paid tickets sold through the
  webshop: claiming a seat from the waiting list for a ticket that costs
  money adds it to the visitor's cart and sends them to checkout, instead
  of confirming the registration for free.

This is a thin bridge module on purpose, kept separate from
``website_event_waiting_list`` itself, so a site with no e-commerce can use
the waiting list without ever installing ``website_event_sale``. It adds no
views, no data and no security rules - purely Python behaviour on top of
the two modules it depends on.

All field technical names are unchanged from the 17.0 module
(``confirmed_from_waiting_list``), so existing data migrates without
remapping.

Usage
=====
* Nothing to configure - once installed alongside ``website_event_sale``,
  any ticket with a price above zero routes through the cart when claimed
  from the waiting list; a free ticket, or a ticket-less event, is
  confirmed directly by ``website_event_waiting_list`` as before.
* The registration stays in the ``wait`` state while checkout/payment is
  in progress, and only becomes ``open`` once the linked sale order is
  actually paid (``state == 'sale'``) - clicking the link never hands out
  a seat for free.
* If the order is cancelled, or the ticket is removed from the cart before
  paying, the registration is sent back to the waiting list (``wait``,
  with the order link cleared) rather than being cancelled outright, so
  the visitor keeps their place in line and can try again.
* If the last seat is claimed by someone else between the confirmation
  email being sent and this visitor's click, the cart add is rejected and
  the same waiting-list management page is re-rendered showing it can no
  longer be claimed, instead of dropping the visitor into an empty cart.
* Joining the waiting list in the first place - even for a free ticket,
  even without this module installed at all - never redirects to
  "/shop/checkout" or "/shop/confirmation": those are
  ``website_event_sale``'s own generic pages for a completed purchase,
  and core has no notion that a registration ending up there might
  actually be in the ``wait`` state rather than genuinely bought. This
  module's ``registration_confirm`` override always has the final say
  and sends a waiting-list join back to this event's own "Joined the
  waiting list!" page instead - see ``controllers/main.py`` for exactly
  why core's own redirect cannot simply be trusted here. The
  registration itself is also kept unlinked from any cart while waiting
  (see ``EventRegistration.create``), even if the visitor happened to
  have an unrelated cart already open from earlier browsing - a
  waiting-list join was never meant to touch the cart in the first
  place, only claiming a seat from it is.

Known issues
============
* If a visitor's cart happened to be open already when they joined the
  waiting list for a free ticket, ``website_event_sale``'s own cart
  logic can still add a stray, zero-price product line for that ticket
  to it before this module gets a chance to stop the registration itself
  from being linked to it. The line is harmless (free, quantity one, not
  tied to any registration) but is not actively cleaned up - it
  disappears the next time that cart is updated or abandoned.

Differences from the 17.0 module
=================================
This is a genuine rewrite, not a straight port - the 17.0 module had two
concrete problems fixed here:

* Its ``models/sale_order.py`` (the code meant to flip a paid waiting-list
  registration from ``wait`` to ``open`` once the order was actually
  confirmed) was **never imported** by that module's ``models/__init__.py``
  - so in the 17.0 codebase that transition never actually ran, and a
  registration confirmed from the waiting list would stay stuck on
  ``wait`` forever, even after being paid for. This is fixed here by
  overriding ``EventRegistration._compute_registration_status`` (the real
  v19 mechanism that drives ``state`` once ``event_sale`` is installed -
  it is a computed field there, not a plain one as in earlier versions)
  so a waiting-list confirmation tracks its order's state correctly:
  ``wait`` while pending, ``open`` once paid.
* Its ``SaleOrderLine._unlink_associated_registrations`` (meant to revert a
  paid waiting-list registration back to ``wait`` if the order/line was
  cancelled or removed from the cart) called a method name that does not
  exist anywhere in core Odoo, in either 17.0 or 19.0 - so that logic
  never fired either, even if the file had been imported. This version
  hooks the two real places this can happen: ``SaleOrder._action_cancel``
  (order cancelled outright) and ``EventRegistration.action_cancel``
  (which ``website_event_sale`` itself calls when a cart quantity decrease
  removes specific registrations, see its ``SaleOrder._cart_update_order_line``).

Also cleaned up along the way:

* No debug ``logging.info(...)`` calls left in the controller (the 17.0
  module had six, printed unconditionally on every request to the
  manage-registration route).
* The cart-add is checked for failure (sold out in the moment between the
  email and the click) instead of assumed to always succeed.
* The 17.0 module's ``_compute_payment_status`` full override (a copy of
  core's own compute, re-implemented from scratch to cope with a
  ``wait``-state registration having no order yet) is not needed here: in
  v19, that field was renamed ``sale_status`` and folded directly into
  ``_compute_registration_status`` itself (the same method this module
  already extends), and it already leaves an order-less registration
  alone rather than mis-reporting it - nothing needs to be duplicated.

Credits

Contributors
------------

* Miika Nissi <miika.nissi@futural.fi>
* Timo Talvitie <timo.talvitie@futural.fi>
* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
