.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================================
Event Ticket Registration Control Module
========================================

* Manages the registration start of the event tickets from the start of the event,
  to prevent early registrations and to give fair access to the tickets.
* An event without tickets gets a free "Standard Ticket" when it is created.
* An event cannot be published without tickets.
* An event that starts in less than 30 days can be published only by the users of the
  group "Publish Events that are < 30 days away on Website".

Configuration
=============
* Add the users who may publish near events to the group "Publish Events that are
  < 30 days away on Website".

Usage
=====
* **Create a new event**: the tickets get a registration start by the start of the
  event.
* **Modify the event date or the tickets**: the registration start of the tickets is
  recalculated. A published event that is less than 2 months away keeps the sales
  that have already been opened, and a new ticket opens like the other tickets. A
  ticket whose registration ends before the new start is left as it is.
* **Publish an event**: the registration start of the tickets is set by the time
  left to the event, and the change is logged in the chatter of the event.

The registration start follows these rules:

* If the event is more than 2 months away, registration starts 1 month before the
  event.
* If the event is between 1 and 2 months away, registration starts 2 weeks after the
  event is published. Until then a placeholder start at the start of the event is
  shown in the backend.
* If the event is less than 1 month away, registration needs a user with the
  additional rights, and it starts when the event is published. Until then a
  placeholder start at the start of the event is shown in the backend.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
