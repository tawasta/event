.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================
Event Ticket Registration: Self or Invite Others
================================================

This module enhances Odoo's event registration system by allowing users to either register themselves for an event or invite others to join the event. It integrates with the existing shopping cart system and enables participants to manage invitations, track their status, and allow recipients to accept invitations through a secure link.

Configuration
=============
Optional help texts for the registration options can be set per website in
Events > Configuration > Settings > Registration options:

* **Help for registering only myself**
* **Help for registering other participants**

The texts are translatable and support formatting such as paragraphs and
lists. When at least one help text is set, it replaces the default hint about
inviting other participants. A help text left empty is not shown, so
installations that do not need guidance keep the registration window
unchanged.

With several websites, select the website in the same settings block before
editing the texts. The texts are stored per language: write and clear them in
each website language separately.

On an event with a waiting list, registering other participants is not
available, so its help text is hidden as well.

Usage
=====
1. **Invite Others**: When registering for an event, users can toggle the "Invite Others" option.
   If help texts are configured, a "Which option should I choose?" box below
   the options explains when to use each one.
2. **Send Invitations**: After registration, users can send invitations from the portal, and track whether they have been accepted or not.
3. **Accept Invitations**: Invitees receive an email with a secure link to accept the invitation and complete their registration.

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
