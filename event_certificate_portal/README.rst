.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Event Certificate Portal
========================

This module extends Odoo Events to support **attendance certificates** with:

* PDF certificate generation
* Download from the portal (My Events)
* Automatic email sending after event completion
* Configurable certificate content and signature

The feature is designed to work seamlessly with the standard Odoo
``event`` and ``website_event`` applications.

Features
========

* Enable certificates per event
* Allow portal users to download their certificate
* Automatically send certificates by email after the event
* Customizable certificate content:
  - duration text
  - lecturer
* Company-level signature configuration
* Secure access control for portal users

Configuration
=============

#. Go to **Event**
#. Open your company
#. Configure certificate signature:
   * Upload signature image
   * Set signatory name
   * Set signatory title

#. Go to **Events → Events**
#. Open or create an event
#. In the **Certificates** tab:
   * Enable *Certificates enabled*
   * Enable *Send certificate by email after event* (optional)
   * Set duration text (optional)
   * Set lecturer (optional)
   * Set training programme (optional)

Usage
=====

Certificate generation
----------------------

* Certificates are available only when:
  - Event has certificates enabled
  - Registration state is **Attended (done)**
  - Event is finished (for email sending)

Portal download
---------------

#. Go to **My Account → My Events**
#. For attended events, click **Download certificate**

Email sending
-------------

* Certificates are automatically sent by scheduled action:
  - Runs every 30 minutes
  - Sends PDF attachment to attendee
  - Marks certificate as sent

Manual printing
---------------

* Open an event registration
* Use the **Print Certificate** action

Technical details
=================

* Model: ``event.registration``
* Report: QWeb PDF (``ir.actions.report``)
* Portal route:

  ``/my/events/registration/<id>/certificate``

* Access control:
  - Only the registration owner (or related partner) can access the certificate
  - Public users are denied

* Email sending:
  - Uses ``mail.template``
  - Attachment generated dynamically per registration

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
   :alt: Futural Oy.
   :target: https://futural.fi/

This module is maintained by Futural Oy.