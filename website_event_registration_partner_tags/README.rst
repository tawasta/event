.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================================
Website Event: Registration Partner Tags
=========================================

* Adds "Customer of" (companies) to events.
* When a registration is confirmed, the companies of the event that the
  contact of the registration does not have yet in "Customer of" are added to
  the contact. Existing companies of the contact are kept.
* A registration is confirmed right away when the event confirms
  registrations automatically, when a free sale order is confirmed, or when
  the invoice of a paid registration is paid. Unfinished registrations, e.g.
  left in the cart, do not add tags.
* Events without "Customer of" companies do not change contacts.
* The module requires res_partner_multicompany, which provides the "Customer
  of" field of the contact.
* The customer tags (res.partner.category) selected in the event before this
  change are not migrated: "Customer of" contains companies, not tags.

Configuration
=============
* Select the companies in "Customer of" on the event form.

Usage
=====
* Register to the event, e.g. on the website as a logged in user.

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
