.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Website Event Filter Fix
========================
This Odoo module modifies the default behavior of ``website.snippet.filter``
to **exclude ``company_id`` domain filtering** for the ``event.event`` model.

This is useful in multi-company setups where events should be shared across
companies on a website without applying the company-based domain restriction.

Features
========

* Overrides the ``_get_company_domain`` method for ``website.snippet.filter``
* Skips ``company_id`` filter **only** for ``event.event`` model
* Keeps standard behavior for all other models

Usage
=====

This module works automatically when installed. No configuration required.

Technical details
=================
\-


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
