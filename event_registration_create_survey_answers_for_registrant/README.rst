.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================================================
Event Registration: Create Survey Answers for Registrant
========================================================

* Allows creating survey answers for event registrations on
  behalf of the participant
* Intended for situations where the event registration is
  created by a backend Odoo user and you want to 
  log answers for the event surveys.

Configuration
=============
* Ensure that the Survey Stage that the survey answer lands in
  by default (e.g. 'In Progress') has the 'Allow Answer Edit' option toggled.
* Ensure that the survey has 'Users can go back' checkbox set

  * You'll likely also want to set survey paging to 
    'One page with all the questions' but this needs to be before after setting
    the above checkbox, or else the paging option gets hidden from UI.

Usage
=====
* Set up an event with some surveys
* Create a participation record for the event
* Start answering the surveys via participation
  form view's Add Survey Answers button

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
