.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Event Ticket Domain Filter
==========================
This Odoo module allows restricting **event ticket visibility and selectability** based on a custom Odoo domain.
It enables finer access control for ticket types in both the backend and the public website.

Users will only be able to select tickets if their partner record matches the configured domain.

Features
========

- Add a domain to each event ticket
- Use the Odoo domain editor to configure conditions (e.g., `[('country_id.code', '=', 'FI')]`)
- Tickets are visible to everyone but only selectable to matching users
- Smart messaging in the frontend for non-selectable tickets
- Fully integrated into the website event registration modal
- Backend support for editing via domain widget

Usage
=====

1. Go to **Events > Tickets**
2. Add a domain in the **Partner filters** field, e.g.::

   [('country_id.code', '=', 'FI')]

3. In the website frontend:
   - All tickets will be visible
   - Users will only be able to **select** tickets that match their domain access
   - Others will see a message: *"You don't have access to select this ticket."*

Technical details
=================

* `user_in_partner_domain` is a computed boolean
* The modal registration template is inherited via XPath to apply the ticket filtering


Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>
* Jarmo Kortetjärvi <jarmo.kortetjarvi@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
