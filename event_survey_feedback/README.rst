.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Event Survey Feedback
======================
* Send a feedback survey to attendees after an event.

This module is the Odoo 19 successor of the feedback-survey part of
``society_event_core`` (17.0), split out as its own module. It does not
depend on ``event_registration_survey``, or vice versa: neither module
knows about the other, so either can be installed alone or together.

Configuration
=============
1. Create a Survey to use as feedback survey.
2. Set it as the "Feedback survey" on the Event (or its Event Type).
3. On the mail templates you want to use to ask for feedback, enable
   "Is Feedback Email".
4. Add one or more entries to the Event's "Communication" schedule using
   those templates - any trigger works ("After each registration",
   "Before/after the event (starts/ends)", including multi-slot events).
   An optional survey can also be set directly on the scheduler entry, to
   use a different survey than the event's default for that specific
   communication.
5. Two ready-made templates are provided: "Event: Feedback survey" and
   "Event: Feedback reminder" - both marked "Is Feedback Email" already.

Usage
=====
When a scheduler using a "Is Feedback Email" template sends its email to a
registration, that registration's "Feedback survey" is set first (from the
scheduler's own survey, falling back to the event's), so the template's
feedback link (``{{ object.survey_start_url }}``) resolves correctly for
that specific attendee. The link is empty until a feedback survey is set,
instead of pointing to a broken URL.

The feedback link goes through
``/survey/start/<survey_token>/event/<event_id>/registration/<registration_id>``
(or, when not tied to one attendee - e.g. a generic/QR-code link on the
event itself - the shorter ``/survey/start/<survey_token>/event/<event_id>``).
Both behave exactly like core's own ``/survey/start/<survey_token>`` (same
validation, resuming, and cookie-based session handling) but also tag the
resulting answer with ``feedback_event_id`` and, when known,
``feedback_registration_id``, so responses can be correlated back to the
event - and the specific attendee - they were about.

That correlation powers:

* A "Feedback" smart button on the Event, showing how many attendees have
  completed the survey, and linking to their answers.
* A "Feedback Answered" (Yes/No) column and filters/group-by on the
  Attendees list and search view, plus a "Has Feedback Survey" filter -
  so exporting or mailing "attendees who haven't answered yet" is a normal
  filtered list, not a manual cross-reference.

Known issues / Roadmap
======================
* All attendees who receive an "Is Feedback Email" communication get the
  same survey assigned; there is no per-attendee override beyond the
  scheduler-level ``feedback_survey_id``.
* A reminder communication is not automatically skipped for attendees who
  already answered - as in the original implementation, that is controlled
  purely by how the scheduler's timing/trigger is configured; the new
  "Feedback Answered" filter makes it straightforward to build a manual
  reminder list, though.
* The ``registration_id`` in the feedback link is a plain sequential ID,
  not a signed token: someone could in principle tamper with it to answer
  under a different attendee of the *same* event (the controller only
  checks the registration belongs to that event). This only affects the
  internal "who answered" bookkeeping, not the confidentiality of any
  other attendee's data - the same trade-off the original implementation
  made for the event-level link.

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
