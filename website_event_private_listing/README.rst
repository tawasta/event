.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Website Event Private Listing
=============================
This module extends the standard Odoo ``website_event`` module by introducing
a dedicated listing for private events.

Private events are separated from the public event listing and exposed through
their own URL. The module reuses the standard website event frontend logic
(filters, search, pager, templates) while restricting the dataset to events
marked as private.

In addition, the module applies SEO protection (noindex) and restricts access
to authenticated users, ensuring that private events are not publicly discoverable.


Configuration
=============

No additional configuration is required.

The module relies on the boolean field:

    is_private_event (event.event)

Make sure you have a module that defines this field
(e.g. ``website_event_private_event``).

Private events should be flagged manually on the event form.


Usage
=====

Private events are exposed through a dedicated route:

- /private-event
- /private-events

Key behavior:

- Only events with ``is_private_event = True`` are displayed
- The page reuses the standard ``website_event.index`` template
- All filters (date, country, tags, search) work as in core
- The listing is protected behind authentication (``auth="user"``)

Public event listing (/event) remains unchanged and does not show private events
(if another module excludes them).

SEO protection:

- Private listing includes HTTP header:

      X-Robots-Tag: noindex, nofollow, noarchive

- Private listing includes HTML meta tag:

      <meta name="robots" content="noindex,nofollow,noarchive"/>

- Event redirect (/event/<event>) adds noindex header for private events

- Registration page (/event/<event>/register):
  - inherits values to inject ``private_event_noindex=True``
  - adds both HTTP header and meta robots protection

Model behavior:

The module adapts the website search domain via:

    event.event._search_get_detail()

When context contains:

    private_event_listing=True

the method:

- removes any existing ``is_private_event`` filters
- enforces:

      ('is_private_event', '=', True)

This ensures compatibility with other modules modifying the domain.

Known issues / Roadmap
======================
- Access control is currently based only on authentication (logged-in users).
  If stricter access is needed (e.g. per partner, group, or token-based),
  additional access rules or controllers should be implemented.

- Direct URLs to private events are still technically accessible if known.
  The module prevents indexing but does not enforce access restrictions
  on individual event pages.

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
