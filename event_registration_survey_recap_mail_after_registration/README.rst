.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================================
Event Registration: Survey Recap E-mail After Registration
==========================================================

* Adds new option to events so that a recap email is sent to the
  participants about the survey answers they entered while 
  registering.
* E-mail sending is handled by a scheduled action which checks
  for confirmed registrations whose surveys have been finished
  and whose events have been configured to trigger sending 
  of recap emails.
* Intended for situations where you want e.g. the registrant to
  double check their answers and report back if there are any
  mistakes in the answers they entered.

Configuration
=============
* Configure the recap email template in Event Settings (otherwise a placeholder email template is used)
* Set the new 'Send Survey Recap to Registrants' checkbox for the events of your choice that have 
  event surveys configured.

Usage
=====
* Register for the event, and you will get a recap e-mail once the cron runs.
* Old registrations do not get recap emails - only those registrations that get confirmed after the 
  'Send Survey Recap to Registrants' will get he recap emails.

Known issues / Roadmap
======================
* This module is a a workaround for not being able to embed the recap info into the 
  automatic event registration email, since when an event registration gets confirmed, 
  the queue jobs of society_event_core may not have yet been processed and therefore
  the survey answer records may not yet have been attached to the event.registration record.

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
