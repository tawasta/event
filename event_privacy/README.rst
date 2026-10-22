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
   to check it before the registration form can be submitted. The server
   checks it too, so a registration cannot be created without the consent
   even by posting the form directly.
3. Attach activities to an Event (or its Event Type, from which new events
   copy them once). An Event with activities always has "Create Partners in
   registration" (from ``partner_event``) enabled, also when the Event is
   created, because a consent needs a partner.

Usage
=====
When an event has ``Privacy`` activities configured, the registration form
shows a checkbox per activity. On registration, a ``privacy.consent`` record
is created for each activity that the partner has no consent for yet. The
consent is recorded for the partner who made the registration. An anonymous
registration has none, so the attendee partner that ``partner_event`` creates
(or finds by email) is used.

An existing consent is updated only when a logged in user registers: the
consents of his own partner follow the checkboxes of the form. An anonymous
registration never changes an existing consent, because the partner is found
by the email typed in the form and anyone could use another person's email.

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
