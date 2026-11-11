.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================================
Event Subscription and Automated Notification Module
====================================================

* Allows portal users to subscribe to events by tags and to receive an automated
  e-mail notification when a new event with a matching tag is published.
* Each event is announced only once, so the subscribers get no duplicate
  notifications.

Configuration
=============
* Automated event notifications are off by default. Before turning them on via
  Settings -> Scheduled actions, you'll likely want to set existing events'
  "Announcement to Interested Contacts Sent" field to avoid sending messages about
  already ongoing events. Afterwards, enable the scheduled action.

Usage
=====
* **User Subscription Management**

  * Portal users click the event tags they are interested in on their contact
    details page (My Account) and save the choice with "Save Address". A selected
    tag is highlighted and has a check mark. The page tells this to the user.
  * The selection can also be edited on the partner form in the back end.

* **Automated Event Notifications**

  * A scheduled task runs periodically to check for newly published events.
  * The system identifies contacts who have subscribed to event tags matching
    those of the new events.
  * The notification e-mails are placed in the mail queue and sent by it.

* **Prevent Duplicate Notifications**

  * The module marks events that have already been announced.
  * Once a notification is sent for an event, it will not be included in future
    emails.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>
* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
