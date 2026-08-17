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

Odoo's normal translation loading keeps any translation that already
exists in the database and only fills in missing ones (see
``odoo.tools.translate.TranslationImporter.save()``). Since
``website_event`` is installed first and already provides a Finnish
translation for every term this module overrides, a plain ``i18n/fi.po``
would silently have no effect. This module therefore uses a
``post_init_hook`` (``hooks.py``) to force-reload its own po file with
``force_overwrite=True`` right after install, which does take effect
regardless of the existing translation.

**Caveat**: ``post_init_hook`` only runs on the module's first install,
not on subsequent updates. If ``i18n/fi.po`` is edited later, re-apply it
via Settings > Translations > Import, selecting Finnish and this module's
po file with "Overwrite Existing Terms" checked (or re-trigger
``post_init_hook`` manually, e.g. from an Odoo shell).

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
