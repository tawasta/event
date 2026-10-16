.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Website Event Waiting List
==========================

Adds a waiting list to events. When the seats of an event, a slot or a ticket
are taken, further registrations join the waiting list instead of being
rejected. When a seat opens up, the waiting attendees are emailed a link where
they can confirm or cancel their registration.

Configuration
=============

Enable *Enable Waiting List* on the event or on the event template, next to
*Limit Registrations*. It is available when the event or its tickets have a
limit.

The module adds two mail schedulers to the events with a waiting list, with
their own email templates:

* *After registering to waiting list*: sent when someone joins the waiting list
* *After more seats are available send to waiting list registrations*: sent
  when a seat opens up. It is run by the scheduled action *Event: Mail
  Scheduler* of Odoo, which is asked to run soon after a registration is
  cancelled or deleted, or when the seats of an event change. It runs every 24
  hours otherwise.

Usage
=====

When all the seats are taken, the event page still offers the *Register* button.
The registrations that do not fit the free seats join the waiting list, also in
the middle of an order: the first ones get the seats and the rest wait. This
works the same whether the seats are limited for the event, for a slot or for a
ticket.

Waiting registrations do not take a seat and do not get the registration mails
or the event reminders. They get the mail about joining the waiting list, and
the mail about the seat that opened up.

The link in the mail opens a page where the attendee can confirm the
registration while a seat is available (the first one who confirms gets it),
or leave the waiting list. The registrations of the waiting list can also be
mailed again from the list of attendees with the action
*Send event confirmation mail*, and confirmed or cancelled by hand.

Known issues / Roadmap
======================
\-

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
