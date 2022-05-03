.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Website Event Sale Waiting List
===============================
* Adds waiting list functionality to Website Event Sale.
* Joining waiting list does not require payment - confirmation link from email redirects to payment.

Configuration
=============
\-

Usage
=====
\-

Known issues / Roadmap
======================
Auto confirmation works as follows:
1. Free events or free tickets are confirmed immediately upon creation.
2. Paid tickets are confirmed once the attached sale order is sent, confirmed or done. In practice this happens once the sale process is completed through the cart.
3. Paid tickets on the waiting list are also confirmed once the attached sale order is sent, confirmed or done. This introduces a known issue where two people could simultaneously confirm their waiting list registration, go into the shopping cart, confirm their purchase and only the first one would get a confirmed registration. While the other one would be left with a confirmed sale order but no registration confirmation.

Credits
=======

Contributors
------------

* Miika Nissi <miika.nissi@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
