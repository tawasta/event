.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
Website Event - Download Event Info PDF
=======================================
* Adds a 'Download Event Info PDF' button to the website's event page sidebar.
* PDF contains event's

  * Name
  * Date
  * Organizer
  * Location
  * Rendered version of the HTML description created with website builder

Configuration
=============
* None needed

Usage
=====
* Print the PDF from the event page sidebar's new button

Known issues / Roadmap
======================
* Some heavy CSS customization is done to the PDF print to get 
  e.g. flexbox-positioned snippets that are in the event's 
  HTML description field to better fit on the PDF page.
  Checking how the PDF looks like during event creation is recommended,
  and if needed, simplifying the website HTML description.

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
