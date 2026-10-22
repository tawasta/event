.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Event Registration Survey
==========================
* Use a Survey as the Event registration form.

Configuration
=============
\-

Usage
=====
1. Create a Survey/Surveys:
    - If Survey has a question with "Save as user firstname", it is used as the Event registration first name.
    - If Survey has a question with "Save as user lastname", it is used as the Event registration last name.
    - If Survey has a question with "Save as user email", it is used as the Event registration email.
    - If Survey has a question with "Save as user phone number", it is used as the Event registration phone number.
2. Attach it/them to an Event. Only the Surveys attached to the Event, and their
   questions, are accepted from the registration form.
3. The counts of answers and answer sheets of an Event follow the answers and
   the state of the registrations, so cancelling a registration updates them.
   The count of answers adds the survey answers to the answers of the
   registration questions (``website_event_questions_view``).
4. On an Event with time slots, the slot chosen in the registration form is
   kept in the registration.
5. The registration form is laid out with Bootstrap form controls: each
   attendee has a "Ticket #" heading, survey pages are shown as section
   headings, short questions are placed two per row and an error is shown as
   text below the question. Choice answers are highlighted like in the
   survey form, and the selected state updates on click.

Known issues / Roadmap
======================
\-

Credits

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy.
