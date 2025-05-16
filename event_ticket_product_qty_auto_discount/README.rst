.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================================
Event: Ticket Product Quantity Auto Discount
============================================

* Define quantity based discounts that get automatically applied when 
  event ticket products get added to cart on website.
* You can already give an automatic discount of a whole order with core's Coupons. 
  This modules is made to solve the use case where a person orders e.g. 
  5 student tickets and 5 standard tickets, and you want to give
  discount only of the standard tickets' total price, not the whole 
  order's total price.

Configuration
=============
* Open a product and set the discount thresholds in the Event Ticket Quantity Discounts tab,
  e.g. 3-5 results in a 10% discount, and 6-10 results in a 20% discount.
* Ensure you have "Grant discounts on sales order lines" enabled in Sale settings

Usage
=====
* Register to an event and proceed to cart
* Discount % gets auto-applied


Known issues / Roadmap
======================
* This module has not been intended to be used together with price lists.
  Test and improve as needed, if your use case requires also price lists.

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
