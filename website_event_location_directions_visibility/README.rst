.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================================
Website Event: Location Directions Visibility
===============================================

* Adds an "Online Location" toggle to the contact form, next to
  "Use as Event Address" (from ``event_filter_address_partners``)
* When an event's location is a partner marked as an online location (e.g.
  Moodle or Teams), the "Get the Direction" button is hidden on the event's
  website page, since there is no physical address to navigate to
* Disabled by default, so existing locations keep showing the button as
  before

Configuration
=============
* On the contact record used as an event's location (e.g. "Moodle" or
  "Teams"), enable "Use as Event Address", then "Online Location"

Usage
=====
* Open an event page on the website to see the effect: if the event's
  location is marked as an online location, the "Get the Direction" button
  no longer appears in the "Location" sidebar block

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
