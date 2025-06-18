.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================================
Event: Individual Invoice Lines when Invoicing Tickets
======================================================

* Splits e.g. line with 3 event tickets into separate invoice lines for each
* Also fetches event name, date and participant name to the invoice line
  description
* Also supports discounting each invoice lines of the same product separately, 
  e.g. ticket 1 gets applied 0%, ticket 2 5% and ticket 3 10% discount.

Configuration
=============
* Set event ticket discounts, if there are any, on the product template form

Usage
=====
* Register to an event, confirm the sale and invoice the sale fully
* Click the new 'Split Event Ticket Invoice Lines' button on the
  invoice form
* Calculate any discounts with the new 'Compute Ticket Quantity Discounts'
  button.


Known issues / Roadmap
======================
* Assumes the linkages between invoice lines and SO lines, as well as
  SO lines and event registrations to be intact. More complex splits
  need to be manually, if e.g. the records have been manually modified
  after the registration -> SO -> invoice process
* Add validation that discount calculation is prohibited if splitting
  has not yet been done.

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
