.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Event Single Ticket Purchase
============================
This module restricts website event registration to **one ticket per order**.

It ensures that users cannot select multiple tickets at once, even when
multiple ticket types are available.

Features
========

- Limits each ticket selection to values **0 or 1**
- Ensures only **one ticket total** can be selected
- Automatically resets the previous selection when a new ticket is chosen
- Disables the registration button unless exactly one ticket is selected

Configuration
=============
\-

Usage
=====
1. Go to an event page on the website
2. Click *Register*
3. Select a ticket

You will only be able to select **one ticket at a time**.

If you select another ticket type, the previous selection will be cleared automatically.

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
