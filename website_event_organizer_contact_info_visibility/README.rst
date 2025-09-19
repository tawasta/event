.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================================================
Website Event: Configurable Organizer Contact Info Visibility
=============================================================

* Set per event if the organizer should be shown, and also more granularly if 
  their phone, mobile and/or email should be shown
* Also serves as a workaround for the qweb contact widget rendering bug
  where email would not appear (https://github.com/odoo/odoo/issues/190009)
* Can be paired with website_event_responsible_contact_info_visibility to
  fine-tune whether to show organization's or responsible person's contact
  info

Configuration
=============
* In event form view, select an organizer, and then what info to show for them 
  on front end

Usage
=====
* Just open an event page on website to see the selected contact fields

Known issues / Roadmap
======================
\-

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
