# -*- coding: utf-8 -*-

# 1. Standard library imports:
import dateutil.parser

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, fields, models, _

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = 'event.event'

    # 2. Fields declaration
    show_track_twitter_hashtags = fields.Boolean(
        string='Show Twitter hashtag',
        help='Show Twitter hashtag in agenda',
    )

    overlapping_location_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping locations',
        compute='_compute_overlapping_location_track_ids',
    )

    overlapping_chairperson_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping chairpersons',
        compute='_compute_overlapping_chairperson_track_ids',
    )

    overlapping_speaker_track_ids = fields.Many2many(
        comodel_name='event.track',
        string='Overlapping speakers',
        compute='_compute_overlapping_speaker_track_ids',
    )

    event_over = fields.Boolean(
        string='Event over',
        compute='_compute_event_over',
    )

    # 3. Default methods
    @api.multi
    def name_get(self):
        # Override the name get to use only the event name as display name

        result = []
        for event in self:
            result.append((event.id, event.name))
        return result

    # 4. Compute and search fields
    @api.depends('track_ids')
    def _compute_overlapping_location_track_ids(self):
        for record in self:
            overlapping = list()

            for track in record.track_ids:
                overlapping += track.overlapping_location_track_ids.ids

            record.overlapping_location_track_ids = overlapping

    @api.depends('track_ids')
    def _compute_overlapping_chairperson_track_ids(self):
        for record in self:
            overlapping = list()

            for track in record.track_ids:
                overlapping += track.overlapping_chairperson_track_ids.ids

            record.overlapping_chairperson_track_ids = overlapping

    @api.depends('track_ids')
    def _compute_overlapping_speaker_track_ids(self):
        for record in self:
            overlapping = list()

            for track in record.track_ids:
                overlapping += track.overlapping_speaker_track_ids.ids

            record.overlapping_speaker_track_ids = overlapping

    def _compute_event_over(self):
        for record in self:
            if record.date_end < fields.Datetime.now():
                record.event_over = True

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def action_cron_generate_breaks(self):
        # Search events that aren't over yet
        events = self.search([('date_end', '>', fields.Datetime.now())])

        for event in events:
            event.action_generate_breaks()

    def action_generate_breaks(self):
        break_type = self.env.ref('event.event_track_type_break')
        track_model = self.env['event.track']

        for record in self:
            # Remove existing auto-generated breaks
            # While a bit counter-intuitive, this is less resource intense
            # than calculating overlapping breaks/tracks and shifting
            # existing breaks
            record.track_ids.filtered(
                lambda t: t.type.code == 'break').unlink()

            locations = record.track_ids.mapped('location_id')

            for location_id in locations:
                tracks = track_model.search([
                    '|',
                    ('location_id', '=', location_id.id),
                    ('location_id', '=', False),
                    ('event_id', '=', record.id),
                    ('date', '!=', False),
                    ('website_published', '=', True),
                ],
                    order='date'
                )

                previous_track_end = False

                for track in tracks:
                    if track.type == break_type:
                        # Skip breaks
                        continue

                    if not previous_track_end \
                            or track.date == previous_track_end:
                        # No break (the next track starts immediately)
                        previous_track_end = track.date_end
                        continue

                    if previous_track_end and \
                            previous_track_end[0:10] != track.date[0:10]:
                        # Different days. No break here
                        previous_track_end = track.date_end
                        continue

                    duration = abs(dateutil.parser.parse(track.date) -
                                   dateutil.parser.parse(previous_track_end))
                    duration = duration.total_seconds() / 3600

                    # Empty slot between tracks. Create a break
                    track_values = dict(
                        event_id=record.id,
                        location_id=location_id.id,
                        name='',
                        date=previous_track_end,
                        duration=duration,
                        type=break_type.id,
                        website_published=True,
                        color=1,
                    )

                    previous_track_end = track.date_end
                    track_model.create(track_values)

    def week_days(self, weekday):
        weekday=int(weekday)
        weekdays = [
            _("Sunday"),
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday")

            ]

        print weekdays
        

        return weekdays[weekday]

    # 8. Business methods
