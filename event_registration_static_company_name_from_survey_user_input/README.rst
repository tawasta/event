.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================================================
Event Registration: Static 'Company Name' Field from Event Survey
=================================================================

* The aim of the module is to get the company name during event signup reliably 
  and not have it affected by core's compute logic or whether the related partner 
  has a parent defined in contact registry or not.
* Removes the _synchronize_partner_values() calls from 
  event registrations' Company Name field value computation.
* Replaces the computation with seeking the value from event survey that 
  gets answered at event signup

Configuration
=============
* Use society_event_core's functionalities to define a survey for an event.
* In one of the survey's questions, check the new 
  'Save as Event Registration's Company Name' option.

Usage
=====
* Sign up to the event and answer the questionnaire at signup as usual
* In backend, the Company Name gets populated based on the answers

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
