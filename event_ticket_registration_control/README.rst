.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================================
Event Ticket Registration Control Module
========================================
This Odoo module automatically manages the registration start date for event tickets based on the event's start date. It ensures that ticket sales begin at an appropriate time to prevent early registrations and ensure fair access to event tickets.

Configuration
=============
* Add relevant users to the 'Publish Events that are less than 30 days away on Website'

Usage
=====
- **Create a new event**:  
  - The system automatically assigns a ticket with a predefined registration start date.

- **Modify the event date**:  
  - Ticket registration start dates are recalculated and updated accordingly.

- **Add new tickets manually**:  
  - The system ensures that their registration start date aligns with the predefined schedule.

The registration start date follows these rules:
- If the event is **more than 2 months away**, registration starts **1 month before** the event.
- If the event is **between 1 and 2 months away**, registration starts **2 weeks before** the event.
- If the event is **less than 1 month away**, registration requires **manual approval** and is set **1-3 days before** the event.


Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@tawasta.fi>
* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: https://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
