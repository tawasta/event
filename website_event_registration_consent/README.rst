.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Event Registration Consent
==========================

Adds token to users which is used to identify attendees.
This is required so additional information (such as consent) can be
asked from the attendee.

This module also contains a basic tempalte for ticket (and report action).
Use this template as a base for customer specific ticket modifications.

Installation
============

Install the module form Settings->Local Modules

Configuration
=============
\-

Usage
=====

Add URL (/event/registration/${object.token}) to email, which is sent in registration.



Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Aleksi Savijoki <aleksi.savijoki@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
