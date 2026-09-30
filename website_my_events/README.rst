.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Website My Events
=================

This module adds an **Events** entry to the customer portal.

Portal users can view their own event registrations from **My Account**. The
portal list follows Odoo's standard portal behavior and supports:

* pagination
* sorting
* grouping
* search
* date filtering
* registration cancellation from the portal

The portal view only shows registrations linked to the current user's partner
and excludes draft registrations.

Features
========

Portal events page
------------------

The module adds a new **Events** portal entry under **My Account**. The entry
shows the portal user's event registrations in a table with event, ticket,
registration, status, and action information.

Registration information
------------------------

Each registration row shows:

* event name
* event start and end dates
* event ticket, when available
* registration status
* registration date
* booker, when available
* cancellation action, when the event allows cancellation

Registration status
-------------------

The registration status is shown using the event registration state:

* Confirmed
* Unconfirmed
* Attended
* Cancelled
* Waiting, only shown for registrations on an event's waiting list (see
  ``website_event_waiting_list``)

Event status
------------

The event itself is also shown with a calculated date-based status:

* Upcoming
* Ongoing
* Ended

This status is calculated from the event start and end dates.

Portal controls
---------------

The Events portal page supports sorting by:

* Newest, by the event's own date
* Event, alphabetically by event name
* Ticket, alphabetically by ticket name
* Status
* Event Status

The Events portal page supports grouping by:

* None
* Event
* Ticket
* Status
* Event Status

The Events portal page supports searching in:

* All
* Event
* Ticket
* Status
* Event Status

Access rights
=============

The module adds portal read access for:

* event registrations
* website visitors

Only registrations linked to the current portal user's partner are displayed.

Configuration
=============

No configuration is needed.

Usage
=====

To use this module:

#. Install the module.
#. Go to the website portal as a portal user.
#. Open **My Account**.
#. Click **Events**.
#. View, search, sort, group, or filter your event registrations.
#. Cancel a registration from the portal when the event allows cancellation.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>
* Miika Nissi <miika.nissi@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy