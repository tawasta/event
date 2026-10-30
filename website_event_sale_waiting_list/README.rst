.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Website Event Sale Waiting List
===============================

Bridges the waiting list (*website_event_waiting_list*) to the paid tickets sold
through the webshop. A seat that opens up for a waiting attendee is paid in the
shop instead of being confirmed for free.

Usage
=====

No configuration is needed. When a waiting attendee confirms a seat of a ticket
that costs money, the ticket is added to the cart and the attendee goes to the
checkout. The registration stays on the waiting list until the order is paid.

* If the order is cancelled, or the ticket is removed from the cart before the
  payment, the registration goes back to the waiting list.
* If the attendee leaves the waiting list while the ticket is in the cart, the
  ticket leaves the cart too.
* If the seat is taken by someone else in the meantime, the cart is not changed
  and the attendee is told that the seat is no longer available.
* When an order contains more tickets than there are seats, the tickets of the
  registrations that join the waiting list are taken out of the cart: they are
  not bought now.
* Free tickets are confirmed by *website_event_waiting_list* as before.

Credits
=======

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
