.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Event Privacy
==============
* Collect privacy consents when registering for an event.

Configuration
=============
1. Define one or more Data Processing Activities (*Privacy > Master Data >
   Activities*) and enable "Show in event" on those relevant for event
   registrations.
2. Optionally mark an activity "Mandatory Answer" to require the registrant
   to check it before the registration form can be submitted.
3. Attach activities to an Event (or its Event Type, from which new events
   copy them once).

Usage
=====
When an event has ``Privacy`` activities configured, the registration form
shows a checkbox per activity. On registration, a ``privacy.consent`` record
is created or updated for each activity, for the partner resolved by core
for that attendee (existing consents are updated rather than duplicated).

Known issues / Roadmap
======================

Credits

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
