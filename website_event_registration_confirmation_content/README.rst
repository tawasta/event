.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================================
Website Event: Registration Confirmation Content
=================================================

* Replaces the English wording of the "Event: Registration Confirmation"
  email (``event.event_subscription``) with a Moodle-specific message
* Replaces the English wording of the "Event: Reminder" email
  (``event.event_reminder``) similarly. Both the "1 week before" and
  "1 day before" reminder schedulers share this same mail template; the
  wording uses ``get_date_range_str()`` so it automatically reads
  "will begin next week", "will begin tomorrow", etc. depending on which
  scheduler actually fired
* Keeps the surrounding email logic of both emails untouched: the branded
  header/footer, the "Cancel registration" link
  (``website_event_cancellation``) and the add-to-calendar links all keep
  working exactly as before
* Replaces the closing signature of both emails with a fixed "TAKK"
  sign-off and a "Questions? Please contact TAKK: verkkokauppa@takk.fi"
  contact block, instead of the organizer-derived signature and contact info
* The event's own organizer contact block (name/email/phone), shown further
  down in both emails, is suppressed for these two emails only, so the
  TAKK contact block above is not duplicated

Configuration
=============
* Nothing to configure: the module only changes the wording of the
  registration confirmation and reminder emails set up by
  ``event_email_customization``

Usage
=====
* Register for any event: the confirmation email received shows the new
  wording
* Wait for a scheduled reminder email (or trigger one manually): it shows
  the new wording too

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
