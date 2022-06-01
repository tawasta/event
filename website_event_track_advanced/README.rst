.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Website Event Track Advanced
============================

Advanced features for Event Track

Features:
   - Submit Event Track Proposals with different types
   - Edit and view Proposals and reviews in portal.
   - Create Review Groups, create reviewers, add reviewers to review groups, link review groups to tracks.
     Review group reviewers can then review tracks in portal with track rating grades and verbal ratings.

Configuration
=============
\-

Usage
=====
\-

Known issues / Roadmap
======================
Migration changes 10.0 -> 14.0:
   - New Model event.track.rating.grade with default grades 1-5
   - event.track.rating rating Integer field replaced with Many2one grade_id field
   - event.track rating Integer field replaced with Many2one grade_id field
   - event.event field event_description removed (use description instead)
   - Moved reviewers from res.partner to event.track.reviewers
   - event.track.rating use reviewer_id over user.uid
   - event.track.review.group reviewers from res.partner to event.track.reviewers
   - event.track.tag tracks field deprecated, use track_ids instead

Credits
=======

Contributors
------------

* Miika Nissi <miika.nissi@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
