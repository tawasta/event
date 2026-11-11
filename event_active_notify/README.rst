.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Event Active Notification
=========================

* Notify members of a designated internal group when an event is activated in Odoo.
* Notify the same group on the day the ticket sale of an event starts.

Configuration
=============
* Assign users to the group **Event Notifications**
  (``event_active_notify.group_event_notifications``) in Settings > Users & Companies > Groups.
* Check the e-mail templates **Event: Activation Notification to Internal Group**
  and **Event: Ticket Sale Starts Today**. They come with the module.
* The scheduled action **Notify Ticket Sales Start** runs once a day.

Usage
=====
* When the ``is_published`` field of an event is set to True (on creation or update),
  all users in the group get an e-mail with the organizer, location, start and end dates.
  An event is announced only once.
* On the day a ticket sale starts, the group gets an e-mail about that event.
  The notification is sent only once per event.

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
