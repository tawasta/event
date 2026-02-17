.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================================
Event Sale: Keep Registrations as Drafts after SO Confirmation
==============================================================

* Adds option to Sale Orders to not autoconfirm event registrations 
  when the SO gets confirmed
* Intended for situations where you manually create event
  registrations to paid events by creating Sale Orders via
  Odoo backend, and you want to modify the event registration
  records before e.g. instant event confirmation emails get
  sent to participants.

Configuration
=============
* None needed

Usage
=====
* Create a new Sale Order that contains event tickets
* Toggle the new "Leave Event Registrations As Drafts" checkbox
* Confirm the Sale Order
* Open one of the created event registration records and see 
  that it remains in Draft state instead of Registered.
* Manually click "Registered" button to confirm the event 
  registration 

Known issues / Roadmap
======================
* Note that due to core's code structure, the
  sale_order_line._init_registrations() function gets overridden
  entirely by this module.

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
