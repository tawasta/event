.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================
Event Ticket Invitations on Order Confirmation
==============================================

* Shows an "Invite the other participants" box on the order confirmation page
  of the web shop when the order has tickets bought for other participants.
* The box has optional instructions and a button to the Events page of the
  customer portal, where the invitations are sent.
* A buyer who is not logged in gets a button that logs in to the order
  customer's account, or creates it, and then opens the Events page.
* While the payment is still pending, the box tells that the invitations can
  be sent once the payment has been confirmed.

Configuration
=============
The instructions are set per website in Events > Configuration > Settings >
Registration options > Invitation instructions after payment. The text is
translatable and supports formatting such as paragraphs, lists and links.
Leave it empty to show only the button.

A buyer who is not logged in and has no account gets the button only when
customers can sign up (Settings > Permissions > Customer Account: Free sign
up). Otherwise the box tells that the invitations are sent from the Events
page of the customer account.

Usage
=====
* Buy an event ticket in the web shop with the option to register other
  participants, and pay the order.
* On the order confirmation page, use the button in the "Invite the other
  participants" box to send the invitations.

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
