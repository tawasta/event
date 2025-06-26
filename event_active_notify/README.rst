.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Event Active Notification
=========================
Notify members of a designated internal group when an event is activated in Odoo.

Configuration
=============
1. Install the module `event_active_notify`.
2. Assign users to the group **Event Notifications** (`event_active_notify.group_event_notifications`) via the Settings > Users & Companies > Groups menu.
3. Ensure the email template **Event: Activation Notification to Internal Group** (`event_active_notify.event_activation_internal_group_mail`) is correctly configured (usually comes with the module).

Usage
=====
- When an event's `is_published` field is set to True (on creation or update), the module automatically sends a notification email to all users in the internal notification group.
- The email includes key event details such as organizer, location, start and end dates.


Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@tawasta.fi>

Maintainer
----------

.. image:: https://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: https://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
