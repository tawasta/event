.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Website Event Track Advanced
============================

A full Call for Proposals (CfP) system for Events: portal-based talk/track
submission, a draft-submit-review-accept workflow, peer review with
ratings, and extensive per-event/per-track-type configuration. Built on
top of Odoo's core ``website_event_track``.

Features
========

* **Portal proposal form**: presenters submit a track (talk) proposal from
  the event page - title, rich-text description, video link, primary
  presentation language plus additional languages they could also present
  in, one or more presenters (name/email/phone/organization/title),
  subtheme, target group(s), tag(s), file attachments, and GDPR/privacy
  consents. The same form is reused for editing a draft and for reviewer
  evaluation.
* **Workshop and webinar sub-forms**: track types can be marked as
  "Workshop" (min/max participants, fee, goals, schedule, requested time
  slot, and - if configured - an organizer/invoicing contract block with
  company details and signee) or "Webinar", with matching form sections
  that show/hide automatically based on the selected track type.
* **Draft -> Submit -> Review -> Accept workflow**: track stages carry
  ``is_draft`` / ``is_editable`` / ``is_submitted`` / ``is_accepted``
  flags that control what a submitter can still edit and when reviewers
  get to see the proposal.
* **Peer review system**: Review Groups group Reviewers (linked to
  ``res.users``); each track is assigned to one review group and every
  reviewer in it can rate the track (1-5 grade + verbal comment). Average
  rating is computed automatically, and a public popup shows the rating
  summary per track.
* **Bulk reviewer assignment**: an "Assign Reviewers" wizard (available on
  selected tracks or on the event) assigns tracks to a review group
  manually, randomly, or evenly distributed across all groups, with an
  option to skip tracks that already have a group.
* **Per-event configuration**: which locations, track types, target
  groups, subthemes and rating scale are offered (pre-filled from the
  Event Type when one is set); whether tags/target groups are single- or
  multi-select; whether to use the ordered "track speakers" list instead
  of a plain presenter list; and toggles to hide the presentation-link,
  attachment or subtheme section of the portal form entirely for a given
  event.
* **Scheduling conflict detection**: tracks sharing the same location,
  chairperson or a speaker, with overlapping date/duration, are
  automatically flagged - both on the track and rolled up on the event
  form.
* **Automatic break generation**: a "Generate Breaks" button fills
  same-day scheduling gaps between sessions per location with
  auto-created, auto-published "Break" tracks.
* **Portal "My Tracks"**: submitters see the status of their own
  proposals; reviewers additionally see tracks awaiting their review, both
  grouped by event.
* **Poster session listing**: a dedicated public page for tracks of the
  "poster" type.
* **Printable room schedule**: a PDF report per location listing its
  tracks in a day-by-day timetable.
* **GDPR/privacy consent tracking**: configurable, optionally required
  consent checkboxes on the proposal form, including an extra consent
  specific to workshop-type submissions.
* **Automated stage emails**: templates for "proposal received", "proposal
  accepted" and "proposal refused" (see *Known issues* - not linked to
  stages out of the box).
* **Website editor toggles**: on the track detail page and agenda cards,
  editors can show/hide the author, show the speaker list (in either
  presenter mode), show the chairperson, and switch between compact and
  detailed location/time display.

Configuration
=============

Event Track Types (Events > CfP Configuration > Track Types) have the
following options:

* **Show in proposals** - whether this type can be selected in the
  submission form.
* **Show in agenda** - whether tracks of this type appear on the
  published agenda.
* **Attendable** - whether this type represents an attendable session
  (unattendable types are shown muted in the agenda).
* **Webinar** - whether tracks of this type can have a webinar.
* **Workshop** - whether tracks of this type have a workshop.
* **Workshop contract** - whether tracks of this type require a signature
  and organization/invoicing details.

Per event (Event form > Event Track Settings tab), configure the allowed
locations/types/target groups/subthemes/rating scale, single- vs.
multi-select for tags and target groups, whether to use the ordered
speaker list, and the "hide presentation link / hide attachment field /
hide subtheme field" portal-form toggles.

Two things need to be set up manually per installation before the module
is fully usable:

* **Track Stage flags and stage-change emails**: the data file that would
  pre-configure ``is_draft``/``is_editable``/``is_submitted``/
  ``is_accepted`` on the default track stages, and link the "Draft" /
  "Announced" / "Refused" email templates to them, is not loaded by
  default. Configure these manually on the Track Stage records (Events >
  CfP Configuration > Track Stages) for the workflow and its emails to
  work.
* **"Proposal submitter can see evaluations" / "Evaluator can see
  attachments"**: these exist as system parameters but have no toggle in
  Settings by default. Set them under Settings > Technical > System
  Parameters, or enable the corresponding (currently commented out) view.

Usage
=====

* From an event's page, click the "Submit a talk" (or similar) button to
  open the proposal form. Save as draft to keep editing later, or submit
  for review.
* Track submitters can follow the status of their proposals from *My
  Account > Tracks*.
* Reviewers rate tracks assigned to their review group either from *My
  Account > Tracks > Review Tracks* or from the backend track form.
* Backend: use the "Assign Reviewers" action on selected tracks (or on the
  event) to distribute tracks across review groups; use "Generate Breaks"
  on the event form to fill schedule gaps; print a location's schedule
  from the Location record.

Known issues / Roadmap
======================

* Track Stage workflow flags and the stage-change email templates are not
  pre-configured out of the box - see *Configuration* above.

Credits
=======

Contributors
------------

* Miika Nissi <miika.nissi@futural.fi>
* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
