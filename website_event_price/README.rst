.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Website Event Price
===================

This module improves the visibility of event ticket pricing on the website.

It adds the event ticket price to:

* the event cards on the event listing page
* the event page sidebar, directly after the registration button and before
  the date and time information

The displayed price is calculated from the active event tickets. If an event has
multiple ticket prices, the lowest price is shown using a "From" prefix. Exact
ticket prices remain available during the normal event registration flow.

For free events, the module displays a clear "Free" label.

Configuration
=============
No configuration is required.

The module uses the website tax display setting to decide whether prices are
shown tax excluded or tax included.

Usage
=====

#. Go to the website event listing page.
#. Open an event card.
#. The event price is shown below the event title.
#. Open the event page.
#. The price is shown in the right-hand sidebar after the registration button.

Price display logic
~~~~~~~~~~~~~~~~~~~

Single paid ticket
    The ticket price is shown directly.

Multiple paid tickets with the same price
    The shared ticket price is shown directly.

Multiple paid tickets with different prices
    The lowest ticket price is shown with the prefix "From".

Free tickets
    The event is shown as "Free".

Known issues / Roadmap
======================

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
