##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:

# 3. Odoo imports (openerp):
from odoo import _, api, fields, models

# 2. Known third party imports:


# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    show_track_twitter_hashtags = fields.Boolean(
        string="Show Twitter hashtag",
        help="Show Twitter hashtag in agenda",
        compute="_compute_show_track_twitter_hashtags",
        store=True,
        readonly=False,
    )

    use_speaker_track = fields.Boolean(
        string="Use speaker track instead of partners", default=False
    )

    location_ids = fields.Many2many(
        "event.track.location",
        string="Locations",
        compute="_compute_location_ids",
        store=True,
        readonly=False,
    )
    track_types_ids = fields.Many2many(
        "event.track.type",
        string="Event track types",
        compute="_compute_track_types_ids",
        store=True,
        readonly=False,
    )
    target_group_ids = fields.Many2many(
        "event.track.target.group",
        string="Target Groups",
        compute="_compute_target_group_ids",
        store=True,
        readonly=False,
    )
    rating_grade_ids = fields.Many2many(
        "event.track.rating.grade",
        relation="event_rating_grades_rel",
        string="Rating Grades",
    )
    overlapping_location_track_ids = fields.Many2many(
        comodel_name="event.track",
        string="Overlapping locations",
        compute="_compute_overlapping_location_track_ids",
    )
    overlapping_chairperson_track_ids = fields.Many2many(
        comodel_name="event.track",
        string="Overlapping chairpersons",
        compute="_compute_overlapping_chairperson_track_ids",
    )
    overlapping_speaker_track_ids = fields.Many2many(
        comodel_name="event.track",
        string="Overlapping speakers",
        compute="_compute_overlapping_speaker_track_ids",
    )
    event_over = fields.Boolean(compute="_compute_event_over")
    allow_track_tags_multiple = fields.Boolean(
        string="Allow Multiple Tags on Tracks", default=True
    )
    allow_target_group_multiple = fields.Boolean(
        string="Allow Multiple Target Groups on Tracks", default=False
    )

    privacy_ids = fields.Many2many(
        "privacy.activity",
        string="Privacies",
        readonly=False,
        store=True,
        default=lambda self: self.env["privacy.activity"]
        .sudo()
        .search([("show_in_event", "=", True)])
        .ids,
    )
    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_type_id")
    def _compute_show_track_twitter_hashtags(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if not event.event_type_id:
                event.show_track_twitter_hashtags = (
                    event.show_track_twitter_hashtags or False
                )
            else:
                event.show_track_twitter_hashtags = (
                    event.event_type_id.show_track_twitter_hashtags or False
                )

    @api.depends("event_type_id")
    def _compute_location_ids(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if not event.event_type_id:
                event.location_ids = event.location_ids or False
            else:
                event.location_ids = event.event_type_id.location_ids or False

    @api.depends("event_type_id")
    def _compute_track_types_ids(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if not event.event_type_id:
                event.track_types_ids = event.track_types_ids or False
            else:
                event.track_types_ids = event.event_type_id.track_types_ids or False

    @api.depends("event_type_id")
    def _compute_target_group_ids(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if not event.event_type_id:
                event.target_group_ids = event.target_group_ids or False
            else:
                event.target_group_ids = event.event_type_id.target_group_ids or False

    @api.depends("track_ids")
    def _compute_overlapping_location_track_ids(self):
        for record in self:
            overlapping = list()
            for track in record.track_ids:
                overlapping += track.overlapping_location_track_ids.ids
            record.overlapping_location_track_ids = overlapping or False

    @api.depends("track_ids")
    def _compute_overlapping_chairperson_track_ids(self):
        for record in self:
            overlapping = list()
            for track in record.track_ids:
                overlapping += track.overlapping_chairperson_track_ids.ids
            record.overlapping_chairperson_track_ids = overlapping or False

    @api.depends("track_ids")
    def _compute_overlapping_speaker_track_ids(self):
        for record in self:
            overlapping = list()
            for track in record.track_ids:
                overlapping += track.overlapping_speaker_track_ids.ids
            record.overlapping_speaker_track_ids = overlapping or False

    def _compute_event_over(self):
        for record in self:
            if record.date_end < fields.Datetime.now():
                record.event_over = True

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    def action_generate_breaks(self):
        break_type = self.env.ref("website_event_track_advanced.event_track_type_break")
        track_model = self.env["event.track"]

        for record in self:
            # Remove existing auto-generated breaks
            # While a bit counter-intuitive, this is less resource intense
            # than calculating overlapping breaks/tracks and shifting
            # existing breaks
            record.track_ids.filtered(lambda t: t.type.code == "break").unlink()

            locations = record.track_ids.mapped("location_id")

            for location_id in locations:
                tracks = track_model.search(
                    [
                        ("location_id", "=", location_id.id),
                        ("event_id", "=", record.id),
                        ("date", "!=", False),
                        ("date_end", "!=", False),
                        ("website_published", "=", True),
                        ("stage_id.is_done", "=", True),
                    ],
                    order="date",
                )

                previous_track_end = False

                for track in tracks:
                    if track.type == break_type:
                        # Skip breaks
                        continue

                    if not previous_track_end or track.date == previous_track_end:
                        # No break (the next track starts immediately)
                        previous_track_end = track.date_end
                        continue

                    if (
                        previous_track_end
                        and previous_track_end.date() != track.date.date()
                    ):
                        # Different days. No break here
                        previous_track_end = track.date_end
                        continue

                    duration = track.date - previous_track_end
                    hours, remainder = divmod(duration.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    if hours > 0 and minutes > 0:
                        break_name = _("Break: %s hours %s minutes") % (hours, minutes)
                    elif hours > 0:
                        break_name = _("Break: %s hours") % (hours)
                    else:
                        break_name = _("Break: %s minutes") % (minutes)

                    duration = duration.total_seconds() / 3600

                    first_done_stage = self.env["event.track.stage"].search(
                        [("is_done", "=", True)], order="sequence"
                    )
                    # Empty slot between tracks. Create a break
                    track_values = dict(
                        event_id=record.id,
                        location_id=location_id.id,
                        name=break_name,
                        date=previous_track_end,
                        duration=duration,
                        type=break_type.id,
                        website_published=True,
                        color=1,
                        stage_id=first_done_stage.id,
                    )

                    previous_track_end = track.date_end
                    track_model.create(track_values)

    def week_days(self, weekday):
        weekday = int(weekday)
        weekdays = [
            _("Sunday"),
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
        ]

        return weekdays[weekday]

    # 8. Business methods
