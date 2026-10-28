.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Event eLearning Integration
===========================

* When attendees are confirmed for an event, they are automatically enrolled into the related elearning channel.

  * Note: Attendee means the Attendee Partner, provided by OCA partner_event module
  * This also covers paid registrations, which are confirmed when their sale order is confirmed
  * A registration sold through a sale order gives course access only once the order is confirmed. This also applies to free tickets, 
    which are confirmed already in the cart.
  * Enrollment and removal are logged in the registration's chatter
  * If the enrollment fails, the order confirmation is not blocked. The error is logged in the registration's chatter instead.
  * Linking a course to an event that already has confirmed registrations autoenrolls the eventattendees. If the course is changed, 
    attendees keep their access to the previous course.
  * Enrollment happens when a registration starts giving course access, or when its attendee changes. Other edits of a 
    registration don't enroll again, so access removed on purpose (e.g. by ``website_slides_channel_auto_remove_participant_after_x_days``) 
    stays removed. An open registration that was not enrolled for some reason is enrolled by setting it back to unconfirmed and confirming it again.

* If the registration is later cancelled, the attendee is also removed from the course.

  * The same applies when a registration is set back to unconfirmed (or moved to the waiting list if `website_event_waiting_list` is used)
  * Deleting a registration that gives course access also removes the attendee from the course.
  * Removal archives the course membership and unsubscribes the attendee from the course's notifications, like leaving the course does. The
    course progress is kept if the attendee joins again.
  * Only cancelling a confirmed registration removes access. Cancelling an unconfirmed registration keeps access the attendee got some other way.
  * The attendee keeps access if they still have another confirmed registration on an event that is linked to the same course
* Additionally, the event registration confirmation email is extended to include a direct link to the related course.

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
* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
