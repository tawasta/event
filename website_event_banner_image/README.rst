.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Website Event Banner Image
==========================
* Ability to add a banner image from backend to an event or event type.
* Banner image is primarily pulled from the event's event type. If event
  type is not set, then from the event itself.
* Note: backend based banner image will always take precedence over a banner
  image that may have been set manually via the website builder. To show the website builder
  based image, you would need to delete the event's backend image.
* For use cases where you expect to be using the website builder to manage the event images,
  it's not recommended to install this module.

Configuration
=============
* Go to event page in backend and set the image. The image will now appear on
  both the event page, as well as any Event widgets that are in use on the website.

Usage
=====
\-

Known issues / Roadmap
======================
- Each image has to be uploaded from users computer (similar to product images).
- No optimization for handling multiples of the same image. Each image is uploaded and handled as a new image.

Credits
=======

Contributors
------------

* Miika Nissi <miika.nissi@futural.fi>
* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
