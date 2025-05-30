.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================================
Event: Access E-mail Template Previews from Event Form
======================================================

* Allow regular users to see mail template preview
* Intended to increase the transparency of what kind of emails get
  sent from events

Configuration
=============
* None needed

Usage
=====
* Create an event with some e-mails configured in the Communication tab.
* Each line now has a preview icon


Known issues / Roadmap
======================
* Currently the module creates an unconfirmed draft event registration and
  uses that in the preview, if no actual registration exists yet. Cron cleans
  up these dummy registration drafts.
* The idea is that the preview always shows an event.registration that actually is
  linked to the event in question, not just the most recent registration 
  record in the DB, like the template preview does by default.

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
