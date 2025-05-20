.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
event ticket domain filter
==========================
This module allows you to restrict event **tickets** based on Odoo domains.

Users will only see tickets that match their partner record based on the defined `paywall_domain`.

Features
========

* Add a domain (`paywall_domain`) per ticket
* Users will only see tickets if their `res.partner` matches the domain
* Integrates with event registration modal (frontend)
* Domain editable using the domain widget in the backend

Usage
=====

1. Go to any Event → Tickets
2. Add a `Paywall Domain` using the domain editor (e.g., `[('country_id.code', '=', 'FI')]`)
3. In the frontend, users will only see tickets they are allowed to see

Technical details
=================

* `paywall_domain` is a CharField (parsed via `safe_eval`)
* `user_in_paywall_domain` is a computed boolean
* The modal registration template is inherited via XPath to apply the ticket filtering


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
