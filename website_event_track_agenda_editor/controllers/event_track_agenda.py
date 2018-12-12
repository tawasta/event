import logging
import re

from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.website_event_track_advanced.controllers.event_track_agenda \
    import WebsiteEventTrackController

_logger = logging.getLogger(__name__)


class WebsiteEventTrackController(WebsiteEventTrackController):

    @http.route(
        ['/event/track/move'],
        type='json',
        auth='public',
        website=True)
    def event_track_move(self, **post):
        # JSON-route for moving tracks

        # Check variables
        old_track_id = post.get('old_track_id', False)
        new_track_id = post.get('new_track_id', False)
        track_model = request.env['event.track']

        try:
            track_model.check_access_rights('read')
            track_model.check_access_rights('write')
        except AccessError:
            _logger.warning('Access error while trying to move a track')
            return 401

        if old_track_id and new_track_id:
            # Strip non numeric characters
            old_track_id = re.sub('[^0-9]', '', old_track_id)
            new_track_id = re.sub('[^0-9]', '', new_track_id)

            old_track = track_model.browse([int(old_track_id)])
            new_track = track_model.browse([int(new_track_id)])

            # Swap the tracks
            old_track.location_id, new_track.location_id = \
                new_track.location_id.id, old_track.location_id.id
            old_track.date, new_track.date = new_track.date, old_track.date

            msg = "Swapped '%s' and '%s'" % (old_track.name, new_track.name)
            _logger.info(msg)

            # Add breaks
            if old_track:
                old_track._calculate_breaks()

            # Add breaks for other location
            try:
                if old_track.location_id != new_track.location_id:
                    new_track._calculate_breaks()
            except MissingError:
                # Nothing to do here
                pass

            return 200
        else:
            _logger.warning('Unexpected error while trying to move a track')
            return 500

    @http.route(
        ['/event/track/unassign'],
        type='json',
        auth='public',
        website=True)
    def event_track_unassign(self, **post):
        # JSON-route for unassigning tracks

        # Check variables
        old_track_id = post.get('old_track_id', False)
        track_model = request.env['event.track']

        try:
            track_model.check_access_rights('read')
            track_model.check_access_rights('write')
        except AccessError:
            _logger.warning('Access error while trying to unassign a track')
            return 401

        if old_track_id:
            # Strip non numeric characters
            old_track_id = re.sub('[^0-9]', '', old_track_id)

            old_track = track_model.browse([int(old_track_id)])
            old_track.date = False

            msg = "Removed '%s' start date" % old_track.name
            _logger.info(msg)

            if old_track:
                old_track._calculate_breaks()

            # Remove unassigned breaks
            if old_track and old_track.type.code == 'break':
                old_track.unlink()

            return 200
        else:
            _logger.warning('Unexpected error while trying to unassign a track')
            return 500

    # Confirm track
    @http.route(
        ['/event/track/schedule'],
        type='http',
        auth='user',
        website=True,
        methods=['POST'])
    def event_track_schedule(self, **post):

        return_url = '/event/'

        track_id = post.get('track_id')

        if track_id:
            track = request.env['event.track'].browse([int(track_id)])

            return_url = '%s%s/agenda' % (return_url, track.event_id.id)

            if post.get('date') and post.get('time'):
                track.date = '%s %s:00' % (post.get('date'), post.get('time'))

            if post.get('location_id'):
                track.location_id = int(post.get('location_id'))

        return request.redirect(return_url)