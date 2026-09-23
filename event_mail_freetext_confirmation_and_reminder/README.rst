.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================================
Event Mail Freetext Confirmation and Reminder
=============================================

This module extends the email templates provided by
the 
module `website_event_cancellation`.

It injects event-specific freetext content into:

* Event registration confirmation emails
* Event reminder emails

The freetext fields are provided by the
``event_mail_freetext_fields`` module.

The module inherits the QWeb email templates from
``website_event_cancellation`` using XPath expressions,
without overriding the original templates.

Configuration
=============

No additional configuration is required.

The module automatically displays the following fields
inside event emails when values are defined on the event:

* ``freetext_confirmation``
* ``freetext_reminder``

Usage
=====

Go to:

* Events
* Open an event
* Fill the confirmation or reminder freetext fields

The content will automatically appear in:

* Registration confirmation emails
* Reminder emails


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
