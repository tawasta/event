.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
Event: Attachment Fields' Container
===================================

* Adds a separate notebook tab for attachment modules' fields
* Intended to be used as dependency for the actual attachment
  related fields to keep the form view cleaner.
* Links the attachments of those fields to their event, so any user
  who can edit the event can also replace the files, not only the
  uploader.

Configuration
=============
* None needed

Usage
=====
* Inherit this module and place new attachment fields into the
  new groups inside the new notebook tab
* Add the new field's name to ``_get_linked_attachment_fields()``
  to link its attachments to the event


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
