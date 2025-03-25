.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================================
Event Subscription and Automated Notification Module
====================================================
This Odoo module allows portal users to subscribe to event categories based on tags and receive automated email notifications when new relevant events are published. The system ensures that users are informed about events they are interested in, while avoiding duplicate notifications.


Configuration
=============
 * Automated event notifications are off by default. Before turning them on via Settings -> Scheduled actions, you'll likely want to set existing events' 
   "Announcement to Interested Contacts Sent" field to avoid sending messages about already ongoing events. Afterwards, enable the scheduled action.

Usage
=====
- **User Subscription Management**:  
  - Portal users can select event tags they are interested in through their profile settings.

- **Automated Event Notifications**:  
  - A scheduled task runs periodically to check for newly published events.
  - The system identifies users who have subscribed to event tags matching those of the new events.
  - Notifications are sent only to users who have not yet received information about a specific event.

- **Prevent Duplicate Notifications**:  
  - The module marks events that have already been included in a notification.
  - Once a notification is sent for an event, it will not be included in future emails for the same users.

Notification Schedule:
- The system checks for new published events and sends notifications every **X hours**.
- Only events that have **not been previously notified** will be included in emails.


Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@tawasta.fi>
* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: https://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
