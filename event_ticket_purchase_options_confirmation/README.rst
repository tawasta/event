.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================
Event Ticket Invitations on Order Confirmation
==============================================

* Shows a "Registrations" box on the order confirmation page of the web shop
  when the order has event registrations, for the buyer or for other
  participants.
* The box has optional instructions and a button to the Events page of the
  customer portal, where the registrations are shown and the invitations to
  the other participants are sent.
* A buyer who is not logged in gets a button that opens the Events page after
  logging in, when the order customer already has an account, or after
  creating the account with the signup link of the order customer.
* While the payment is still pending, the box tells that the registrations are
  shown once the payment has been confirmed.

Configuration
=============
The instructions are set per website in Events > Configuration > Settings >
Registration options > Instructions on order confirmation, for example where
the registrations are found and how the other participants are invited. The
text is translatable and supports formatting such as paragraphs, lists and
links. Leave it empty to show only the button.

A buyer who is not logged in gets a login button when the order customer or
the email of the order already has an account. Without an account the buyer
gets the signup button only when customers can sign up on the website
(Website > Configuration > Settings > Privacy > Customer Account: Free sign
up). Otherwise the box tells that the registrations are shown on the Events
page of the customer account.

While any registration of the order still waits for the payment, the box shows
no button, as the registrations page lists only confirmed registrations.

Usage
=====
* Buy an event ticket in the web shop, for yourself or for other
  participants, and pay the order.
* On the order confirmation page, use the button in the "Registrations" box
  to see the registrations and to invite the other participants.

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
