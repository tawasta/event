.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Website Event Waiting List
==========================
* Adds a waiting list to Events: when sold out, further registrations join
  a waiting list instead of being rejected, and get emailed a confirmation
  link when a seat opens up.

This module is the Odoo 19 successor of the same-named module in the
``17.0`` ``mpg/event`` repo. It only depends on ``website_event`` - not
even ``website_event_cancellation``, despite offering a very similar
"manage my registration via an emailed link" mechanism for waiting-list
attendees: it has its own token field (``waiting_list_access_token``), its
own route and page, and its own email header/footer template, all kept
deliberately separate rather than reused from that other module. This
means it installs directly on bare core ``website_event``, and has zero
awareness of ``event_registration_survey``, ``website_event_cancellation``,
or any other module, in any direction - each can be installed alone or in
any combination.

All field technical names are unchanged from the 17.0 module
(``waiting_list``, ``seats_waiting``, ``waiting_list_to_confirm``, the
``wait`` registration state, the ``after_wait``/``after_seats_available``
scheduler trigger types) so existing data migrates without remapping.

Configuration
=============
* Enable "Enable Waiting List" on an Event (or its Event Type) - only
  available once "Limit Registrations" is on.
* Two mail templates are provided out of the box, already attached as
  scheduler entries on new Event Types: "Event: Waiting List Confirmation"
  (sent immediately when someone joins the waiting list) and "Event:
  Waiting List Open Seats" (sent immediately once a seat frees up for an
  eligible waiting attendee).

Usage
=====
* When an event is sold out (event- or ticket-level) and has the waiting
  list enabled, the registration page offers a "Join the waiting list"
  option instead of just showing "Sold Out".
* Waiting registrations are internally in the ``wait`` state. They do not
  count against seat availability, so they never block otherwise-eligible
  registrations.
* When a seat becomes free, eligible waiting attendees (event and ticket
  both actually available) are emailed immediately with a link to confirm
  or cancel their spot. If seats become unavailable again before they
  respond, and later free up once more, they are notified again.
* A manual "Send event confirmation mail" action is available from the
  Attendees list (select registrations, then the action) for an
  admin-triggered resend.

Known issues / Roadmap
======================
* The waiting-list quantity selector reuses core's own ticket-quantity
  widget markup and CSS classes (``o_wevent_input_nb_tickets``,
  ``data-increment-type``) so that core's existing ``TicketDetails``
  interaction handles the +/- buttons and submit-button enablement with no
  extra JavaScript - this module ships no custom frontend JS at all. If
  core's markup for that widget changes, this integration point would need
  a matching update.
* ``event.event.ticket.seats_waiting`` and ``event.event.ticket.waiting_list``
  from the 17.0 module were dropped: neither was ever referenced by any
  view, template or other module there (the ticket-level seat count was
  explicitly commented "broken" and disabled in 17.0's own source), so
  they were dead fields, not a feature regression.
* Unrelated to this module, but noticed while researching it:
  ``website_event_cancellation``'s own ``event.mail``/``event.mail.registration``
  overrides (``check_and_send_mail``, ``event.mail.registration.execute()``)
  target methods that no longer exist / are no longer called by core's
  redesigned scheduler in 19.0, so they are dead code there; and its
  ``event.event_subscription`` template override
  (``data/email_template_data.xml``) uses old Mako-style ``${...}``
  interpolation in the ``subject`` field, which modern ``mail.template``
  does not render. Neither affects this module in any way (no dependency,
  no shared code path) - just worth knowing if working on that module too.
* The 17.0 ``website_event_sale_waiting_list`` module (routes a waiting-list
  confirmation through ``website_event_sale``'s cart/checkout for paid
  tickets) has not been ported yet. It should stay a separate, thin bridge
  module depending on both this one and ``website_event_sale`` - not merged
  into this one, which would force a sale-order dependency onto anyone who
  just wants a waiting list for free events.

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
