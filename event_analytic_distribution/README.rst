.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
Event: Analytic Distribution Support
====================================

* Adds event and event ticket support to analytic distributions
* Standard Odoo logic for seeking for the best matching analytic
  distribution is used, but event and ticket can be used as 
  additional criteria.
* Intended for situations where the product of an event ticket is not
  enough for analytic accounting (e.g. same ticket product is used
  for multiple events but those events should be allocated 
  differently in analytic accounting)

Configuration
=============

* Add an analytic distribution model via Invoicing -> Configuration
  -> Analytic Distribution Models, and configure it to be based on
  the relevant event and/or event ticket.
* When configuring your event, you can see at the top of the form
  if there is an analytic distribution model that matches the event
  itself or its tickets, or if perhaps a new model should be created.

Usage
=====
* Sell a ticket to the event and invoice it. The analytic distribution
  will be set to both the SO and invoice lines.

Known issues / Roadmap
======================
* None

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
