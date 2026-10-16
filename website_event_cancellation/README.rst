.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Website Event Cancellation
==========================

Lets attendees cancel their own event registration from a personal link in
the registration emails.

* Adds an "Allow Cancellation" setting to events and event templates, next to
  "Limit Registrations"
* Adds a personal, secret registration management link to the registration
  confirmation and reminder emails.
* The link opens a page that shows the status of the registration, the event
  details, the location, the attendee information and what the attendee can do
  next:

  * while cancelling is allowed: the deadline and a *Cancel registration*
    button that asks for a confirmation
  * when the deadline has passed: a note and the email of the organizer
  * when the registration is cancelled: a *Register again* button, if the
    registration of the event is open

* Cancelling is done with a protected POST request. The rules (cancelling
  allowed, deadline, registration state) are checked on the server and not
  only on the page.
* Fixes the date, language and recipient of the standard registration and
  reminder emails and adds calendar links (Google, iCal/Outlook, Yahoo) that
  follow the slot of the registration.

Configuration
=============

* Event template: enable *Allow Cancellation* and set how long before the
  event the attendee can still cancel.
* Event: the values are copied from the template when it is chosen and can be
  changed on the event, next to *Limit Registrations*.

Usage
=====

#. Attendees receive the cancellation link in the confirmation and reminder
   emails (``Registration > Public link`` on the registration).
#. The link shows the registration. Before the deadline, the attendee can
   cancel it from the page. After the deadline, or when the event does not
   allow cancelling, the page only shows the information.
#. Cancelling an event itself is done with the standard Odoo event status
   *Cancelled*. This closes registrations and stops automated emails.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Miika Nissi <miika.nissi@futural.fi>
* Valtteri Lattu <valtteri.lattu@futural.fi>
* Timo Talvitie <timo.talvitie@futural.fi>
* Joona Isoaho <joona.isoaho@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
