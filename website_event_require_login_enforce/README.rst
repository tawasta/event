.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================
Website Event: Enforce Required Login
=====================================

* Extends ``website_event_require_login``.
* For events that require login, logged out users see a login button instead
  of the ticket selection, so they are asked to log in before choosing tickets.
* Registrations of logged out users are refused on the server when they are
  confirmed. This also covers stale pages, expired sessions and direct form
  posts. The user is redirected to log in and back to the event.

Configuration
=============
* Enable "Require login for website registrations" on the event.

Usage
=====
* Open an event that requires login on the website while logged out.

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
