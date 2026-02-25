.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================
Link partner to events: Prioritize users/persons
================================================

* In OCA's partner_event, when finding a partner that matches a given email address, simply the first matching partner
  is used
* This may cause issues when there are multiple partners with the same email address in the DB and you are e.g.
  creating a user account for the found partner: if another partner has the same email AND already has a user 
  account, another account can't (and shouldn't) be created, and an error would be raised.
* This module reworks the _update_attendee_partner_id() function to 

  * Primarily seek a partner with the same email and an existing user account
  * Secondarily seek a partner with the same email and that is a contact (not a company)
  * Finally as a fallback, whatever partner has the same e-mail address (i.e. same as in OCA partner_event)

Configuration
=============
* None needed

Usage
=====
* The module works in the background

Known issues / Roadmap
======================
* Be aware that _update_attendee_partner_id() is completely rewritten by this module, as the logic
  of the partner searching is not overrideable separately

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
