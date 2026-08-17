.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================================
Website Event: Finnish Wording (Koulutus)
=========================================

Overrides ``website_event``'s own Finnish translations so that "tapahtuma"
("event") is replaced with "koulutus" ("training/course") throughout the
website event pages, snippets, tours and related field/model labels.

This module ships its own ``i18n/fi.po``, containing only the 65 entries
from ``website_event``'s own Finnish translation that mention "tapahtuma".
Since Odoo resolves a translation by (language, source text, location) and
not by which module supplied it, installing this module after
``website_event`` (it depends on it) makes these specific Finnish strings
resolve to the "koulutus"-based wording instead, while everything else
(including English and all other languages) is untouched.

Scope: only ``website_event``'s own strings are covered (the public
website pages: event list, event page, registration, snippets, onboarding
tour). The backend ``event`` app's own terminology (e.g. the Events menu,
list/form views used by staff) is intentionally out of scope and keeps
saying "tapahtuma".

Configuration
=============
\-

Usage
=====
Install this module. No further configuration is needed; the Finnish
website event pages will show "koulutus"-based wording immediately.

Known issues / Roadmap
======================
* Only covers ``website_event``'s own translated strings. If other
  installed addons (e.g. ``website_event_sale``) add further
  "tapahtuma"-related Finnish strings, those are not covered by this
  module.

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
