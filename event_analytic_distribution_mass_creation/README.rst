.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Event: Analytic Distribution Mass Creation
==========================================

* Adds "event tag + analytic account" rule configuration option to 
  event ticket products
* Adds a "Generate Analytic Distributions" button to events. It creates
  an analytic distribution model for each ticket of the event, based on
  the tags of the event and the rules of the ticket's product.
* Intended for situations where the same ticket product is used for
  several events that are allocated differently in analytic accounting,
  and where events have so many tickets that adding the analytic
  distribution models one by one is not feasible.

Configuration
=============

* Go to Events -> Configuration -> Event Tags Categories and enable
  "Use in Analytic Accounting Rules" for the categories whose tags can be
  selected in the rules.
* Open an event ticket product and in the "Event Analytic Accounting"
  tab add a line for each event tag that should have its own analytic
  account.
* Optionally, go to Events -> Configuration -> Settings -> Analytic
  Accounting, enable "Create Event Analytic Accounts" and select the
  analytic plan for them. With this setting, the created analytic 
  distributions will be based on two dimensions. 

Usage
=====

* Set the tags and the tickets of an event and click "Generate Analytic
  Distributions".
* For each ticket, the rule of the ticket's product for that tag is
  searched for. If found, an analytic distribution
  model is created for the event + ticket combination, with 100%
  allocated to the analytic account of the rule.
* If event analytic accounts are enabled in the settings, the event gets
  its own analytic account in the selected plan. Each generated analytic
  distribution model then allocates 100% to the rule's analytic account
  and 100% to the event's analytic account, on the same distribution line.
* The generation result log is stored as an internal note in the chatter 
  of the event, containing the created, updated and removed analytic 
  distribution models and the skipped tickets.
* Clicking the button again updates the analytic distribution to match the 
  current tag, rules and settings, and removes them if there are no longer
  matching rules for the product + event tag combination.
* If the event's tag, a ticket's product, a product rule or the event
  analytic account setting changes after generation, a warning at the
  top of the event form tells that the analytic distributions are
  outdated and that the generation button must be re-clicked. 
* Re-clicking the generation button has no effec on existing Sale Orders
  or invoices.
* Analytic distribution generation for a ticket is skipped, if

  * it has a manually maintained analytic distribution model for the event
  * its product has no rule for the event's tag

Known issues / Roadmap
======================

* This module currently always assumes a 100% distribution per analytic
  account, consider adding support for other percentages as well.
* The outdated warning is shown only when the event is opened. A rule
  changed on a product affects all events using it.


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
