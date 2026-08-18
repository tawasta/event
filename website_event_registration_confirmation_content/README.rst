.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================================
Website Event: Registration Confirmation Content
=================================================

* Replaces the English wording of the "Event: Registration Confirmation"
  email (``event.event_subscription``) with a Moodle-specific message
* Keeps the surrounding email logic untouched: the branded header/footer,
  the "Cancel registration" link (``website_event_cancellation``) and the
  add-to-calendar links all keep working exactly as before
* Replaces the closing signature with a fixed "TAKK" sign-off and a
  "Questions? Please contact TAKK: verkkokauppa@takk.fi" contact block,
  instead of the organizer-derived signature and contact info
* The event's own organizer contact block (name/email/phone), shown further
  down in the email, is suppressed for this specific email only, so the
  TAKK contact block above is not duplicated. The reminder email, which
  shares the same underlying template, is unaffected

Configuration
=============
* Nothing to configure: the module only changes the wording of the
  registration confirmation email set up by ``event_email_customization``

Usage
=====
* Register for any event: the confirmation email received shows the new
  wording

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
