.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Website Event Waiting List
==========================
* This module adds a waiting list functionality to Events. When on waiting list and free seats become available, an email with a confirmation link is sent.
* Extends website_event_cancellation to allow cancellation/confirmation of registrations through a url link sent by email.

Configuration
=============
\-

Usage
=====
* Enable waiting list for an event by toggling it on event view.
* When maximum attendees to an event is reached, further registrations go to a waiting list.
* If tickets are used and ticket is sold out, registrations go to waiting list.
* You can attach an email scheduler to an Event to send automatic emails to waiting list when more seats are available

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Miika Nissi <miika.nissi@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
