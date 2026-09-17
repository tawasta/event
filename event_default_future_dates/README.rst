.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================================
Event: Default Event Dates are in the Future
============================================

* New and duplicated events' dates default to future instead of today
* Intended for situations where e.g. an event created for today would 
  have scheduled communications (e.g. default event reminder emails) be
  already in the past. If the event mail scheduler happens to run, it would 
  mark those communications already as dealt with, since the user has not 
  moved the event to the correct date yet. The risk of this increases
  the more frequently the event mail scheduler is configured to be run.
* Defaulting to a date well ahead keeps those communications scheduled 
  until the user has actually set the real dates of the event.

Configuration
=============
* The offset is one month by default. To change it, set the system parameter
  "event_default_future_dates.months" with the integer of your choice.

Usage
=====
* Create or duplicate an event. The start and end dates are prefilled X months
  ahead, but keeping the duration of the original in the case of a duplicate. 
* An event created with an explicit date, for example by clicking a day in the
  calendar view, still keeps the date that was asked for.

Known issues / Roadmap
======================
* None

Credits
=======

Contributors
------------

* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
