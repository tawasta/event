.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Event eLearning Integration
===========================

This module provides a seamless integration between Events and eLearning (Slides) in Odoo.  
When attendees are confirmed for an event, they are automatically enrolled into a related online course.  
If the registration is later cancelled, the attendee is also removed from the course.

Additionally, the event registration confirmation email is extended to include a direct link to the related course.

Features
========

- Link an `event.event` to a `slide.channel` (course).
- Automatically enroll attendees in the related course when their registration is confirmed.
- Automatically remove attendees from the course if they cancel their registration.
- Show the course membership status directly on the event registration form.
- Extend confirmation emails with a link to the course if configured.

Configuration
=============

1. Go to an event form view.
2. Select a related eLearning course in the "Related Course" field.
3. When attendees register and their state becomes **confirmed**, they will be enrolled into the selected course.

Usage
=====

- Register an attendee to an event.
- When the registration is confirmed (state = `open`), the partner will be enrolled in the linked course.
- If the registration is later cancelled (state = `cancel`), the attendee will be removed from the course.
- Confirmation emails will include a course access block, if a course is linked to the event.

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
