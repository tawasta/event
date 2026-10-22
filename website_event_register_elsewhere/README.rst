.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Website Event Register Elsewhere
================================

Lets an event be registered to on another website. The Register button of the
event leads to a link, and the registrations are not made in Odoo.

Configuration
=============

Enable *Register Elsewhere* on the event or on the event template, next to
*Limit Registrations*, and enter the registration link. The link must start with
http:// or https://. The event copies the values from the template when it is
chosen.

Usage
=====

The event page shows a Register button that opens the link in a new tab. The
buttons and the registration form of Odoo are not shown, and the routes of the
registration of the website are closed: a visitor who sends them directly is
redirected to the link. The event is open until it is cancelled or over, and its
seats and tickets are not used. The seats of the event are not shown on the page
either. Registrations made in the backend still work.

Credits
=======

Contributors
------------

* Miika Nissi <miika.nissi@futural.fi>
* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
