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

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import api, fields, models

# 4. Imports from Odoo modules:
from odoo.tools import html2plaintext

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class EventTrack(models.Model):
    # 1. Private attributes
    _inherit = "event.track"

    # 2. Fields declaration
    partner_id = fields.Many2one(string="Contact")
    speaker_ids = fields.Many2many("res.partner", string="Speakers")

    track_speaker_ids = fields.One2many(
        comodel_name="event.track.speaker", inverse_name="track_id", string="Speakers"
    )
    use_speaker_track = fields.Boolean(related="event_id.use_speaker_track")
    chairperson_id = fields.Many2one(
        comodel_name="res.partner",
        string="Chairperson",
        domain=[("is_company", "=", False)],
    )
    organizer = fields.Many2one(comodel_name="res.partner", string="Organizer")
    organizer_contact = fields.Many2one(
        comodel_name="res.partner", string="Organizer contact"
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        domain=[("res_model", "=", "event.track")],
        string="Attachments",
    )
    application_file = fields.Binary(string="Application File")
    application_file_filename = fields.Char(string="Application filename")
    description_plain = fields.Text(
        string="Plain description", compute="_compute_description_plain"
    )

    is_rated = fields.Boolean(
        "Is Rated",
        help="Helper field to check if current user has reviewed the track.",
        compute="_compute_is_rated",
    )
    ratings = fields.One2many("event.track.rating", "event_track", string="Ratings")
    ratings_count = fields.Integer("Ratings Count", compute="_compute_ratings_count")
    rating_avg = fields.Float(
        "Average rating",
        digits=(3, 2),
        compute="_compute_rating_avg",
        store=False,
        copy=False,
    )
    grade_id = fields.Many2one(
        "event.track.rating.grade",
        index=True,
        store=False,
        string="Rating",
        compute="_compute_user_rating",
        inverse="_inverse_user_rating",
    )
    rating_comment = fields.Char(
        string="Verbal Rating",
        store=False,
        compute="_compute_user_rating",
        inverse="_inverse_user_rating",
    )

    type = fields.Many2one(
        comodel_name="event.track.type", inverse_name="event_track", string="Type"
    )

    target_group = fields.Many2one(
        comodel_name="event.track.target.group",
        relation="event_track",
        string="Target group",
    )

    target_group_ids = fields.Many2many(
        comodel_name="event.track.target.group",
        string="Target groups",
    )
    target_group_info = fields.Html(string="Target group info")

    review_group = fields.Many2one(
        comodel_name="event.track.review.group", string="Review Group"
    )
    reviewers = fields.Many2many(
        comodel_name="event.track.reviewer",
        string="Reviewers",
        compute="_compute_reviewers",
    )
    is_reviewer = fields.Boolean(
        "Is reviewer",
        compute="_compute_is_reviewer",
        help="Helper field to check if current user is a reviewer.",
    )

    show_in_agenda = fields.Boolean(
        string="Shown in agenda", compute="_compute_show_in_agenda"
    )

    request_time = fields.Many2one(
        comodel_name="event.track.request.time",
        string="Desired duration of the workshop",
    )

    language = fields.Many2one(comodel_name="res.lang", string="Language")
    keywords = fields.Text(string="Keywords", help="Text keywords")
    extra_info = fields.Html(string="Extra info")
    video_url = fields.Char(string="Track as a video (link to e.g. Youtube or Vimeo)")
    is_webinar = fields.Boolean(related="type.webinar")
    is_workshop = fields.Boolean(related="type.workshop")
    webinar = fields.Boolean(string="Pre-event webinar")
    webinar_info = fields.Html(string="Pre-event webinar info")
    workshop_goals = fields.Html(string="Goals")
    workshop_schedule = fields.Html(string="Schedule")
    workshop_participants = fields.Integer(string="Max participants")
    workshop_min_participants = fields.Integer(string="Min participants")
    workshop_fee = fields.Text(
        string="Workshop participation fee", help="Leave empty for free workshops"
    )
    partner_string = fields.Text(string="Partner", compute="_compute_partner_string")
    speakers_string = fields.Text(string="Speakers", compute="_compute_speakers_string")
    track_speakers_string = fields.Text(
        string="Speakers", compute="_compute_track_speakers_string"
    )
    external_registration = fields.Char(string="External registration link")
    twitter_hashtag = fields.Char(
        string="Twitter hashtag",
        compute="_compute_twitter_hashtag",
        store=True,
        copy=False,
    )
    extra_materials = fields.Html(
        string="Extra materials",
        help="Extra materials (links etc.) that are shown in agenda",
    )
    extra_materials_plain = fields.Text(
        string="Plain extra_materials", compute="_compute_extra_materials_plain"
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
    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("description")
    def _compute_description_plain(self):
        for record in self:
            if record.description:
                record.description_plain = html2plaintext(record.description)
            else:
                record.description_plain = ""

    def _compute_show_in_agenda(self):
        for record in self:
            location_show = record.location_id.show_in_agenda or False
            type_show = record.type.show_in_agenda or False
            show_in_agenda = location_show and type_show
            record.show_in_agenda = show_in_agenda or False

    def _compute_partner_string(self):
        for record in self:
            record.partner_string = record.partner_id.name or False

    def _compute_speakers_string(self):
        for record in self:
            speakers = ""
            for speaker in record.speaker_ids:
                speakers += " %s," % speaker.display_name
            speakers = speakers[1:-1]
            record.speakers_string = speakers or False

    def _compute_track_speakers_string(self):
        for record in self:
            speakers = ""
            for speaker in record.track_speaker_ids:
                speakers += " %s," % speaker.partner_id.display_name
            speakers = speakers[1:-1]
            record.track_speakers_string = speakers or False

    @api.depends("type.twitter_hashtag")
    def _compute_twitter_hashtag(self):
        for record in self:
            hashtag = ""
            if record.type.twitter_hashtag:
                hashtag = "{}{}".format(record.type.twitter_hashtag, record.id)
            record.twitter_hashtag = hashtag or False

    @api.depends("extra_materials")
    def _compute_extra_materials_plain(self):
        for record in self:
            if record.extra_materials:
                record.extra_materials_plain = html2plaintext(record.extra_materials)
            else:
                record.extra_materials_plain = ""

    @api.depends("review_group")
    def _compute_reviewers(self):
        for rec in self:
            if rec.review_group:
                rec.reviewers = self.env["event.track.reviewer"].search(
                    [("review_group_ids", "=", rec.review_group.id)]
                )
            else:
                rec.reviewers = False

    def _compute_is_reviewer(self):
        for rec in self:
            rec.is_reviewer = False
            for reviewer in rec.reviewers:
                if self.env.user == reviewer.user_id:
                    rec.is_reviewer = True
                    return

    def _compute_ratings_count(self):
        for rec in self:
            rec.ratings_count = len(rec.ratings) or 0

    def _compute_rating_avg(self):
        for rec in self:
            rating_avg = 0
            if rec.ratings:
                ratings_sum = 0
                for rating in rec.ratings:
                    ratings_sum += rating.grade_id.grade
                rating_avg = float(ratings_sum) / float(rec.ratings_count)
            rec.rating_avg = rating_avg

    def _compute_user_rating(self):
        for rec in self:
            reviewer = self.env["event.track.reviewer"].search(
                [("user_id", "=", rec.env.user.id)]
            )
            if reviewer:
                existing_rating = rec.ratings.search(
                    [("reviewer_id", "=", reviewer.id), ("event_track", "=", rec.id)]
                )
                if existing_rating:
                    rec.grade_id = existing_rating.grade_id
                    rec.rating_comment = existing_rating.comment
            else:
                rec.grade_id = False
                rec.rating_comment = False

    def _inverse_user_rating(self):
        for rec in self:
            reviewer = self.env["event.track.reviewer"].search(
                [("user_id", "=", rec.env.user.id)]
            )
            if not reviewer:
                reviewer = self.env["event.track.reviewer"].create(
                    {"user_id": rec.env.user.id}
                )
            existing_rating = rec.ratings.search(
                [("reviewer_id", "=", reviewer.id), ("event_track", "=", rec.id)]
            )
            if existing_rating:
                if rec.grade_id:
                    existing_rating.grade_id = rec.grade_id
                if rec.rating_comment:
                    existing_rating.comment = rec.rating_comment
            else:
                rec.ratings.create(
                    {
                        "event_track": rec.id,
                        "reviewer_id": reviewer.id,
                        "grade_id": rec.grade_id.id,
                        "comment": rec.rating_comment,
                    }
                )

    def _compute_is_rated(self):
        for rec in self:
            rec.is_rated = False
            reviewer = self.env["event.track.reviewer"].search(
                [("user_id", "=", rec.env.user.id)]
            )
            if reviewer:
                existing_rating = rec.ratings.search(
                    [("reviewer_id", "=", reviewer.id), ("event_track", "=", rec.id)]
                )
                if existing_rating:
                    rec.is_rated = True

    def _compute_overlapping_location_track_ids(self):
        # Search overlapping tracks in the same location
        EventTrack = self.env["event.track"]
        for record in self:
            if not record.location_id or not record.date or not record.duration:
                # If all the necessary information is not set, skip this
                record.overlapping_location_track_ids = False
                continue
            domain = list()
            if not isinstance(record.id, models.NewId):
                # Exclude the record itself
                domain.append(("id", "!=", record.id))
            domain += [
                # Same location
                ("location_id", "!=", False),
                ("location_id", "=", record.location_id.id),
                # Starts before this ends
                ("date", "<", record.date_end),
                # Ends after this starts
                ("date_end", ">", record.date),
            ]
            overlapping_tracks = EventTrack.search(domain)
            overlapping_tracks = overlapping_tracks.filtered(
                lambda t: t.id != record.id
            )
            if overlapping_tracks:
                record.overlapping_location_track_ids = overlapping_tracks.ids
            else:
                record.overlapping_location_track_ids = False

    def _compute_overlapping_chairperson_track_ids(self):
        EventTrack = self.env["event.track"]
        for record in self:
            if not record.chairperson_id or not record.date or not record.duration:
                # If all the necessary information is not set, skip this
                record.overlapping_chairperson_track_ids = False
                continue
            domain = list()
            if not isinstance(record.id, models.NewId):
                # Exclude the record itself
                domain.append(("id", "!=", record.id))
            domain += [
                # Same chairperson
                ("chairperson_id", "!=", False),
                ("chairperson_id", "=", record.chairperson_id.id),
                # Starts before this ends
                ("date", "<", record.date_end),
                # Ends after this starts
                ("date_end", ">", record.date),
            ]
            overlapping_tracks = EventTrack.search(domain)
            if overlapping_tracks:
                record.overlapping_chairperson_track_ids = overlapping_tracks.ids
            else:
                record.overlapping_chairperson_track_ids = False

    def _compute_overlapping_speaker_track_ids(self):
        EventTrack = self.env["event.track"]
        for record in self:
            if not record.speaker_ids or not record.date or not record.duration:
                # If all the necessary information is not set, skip this
                record.overlapping_speaker_track_ids = False
                continue
            domain = list()
            if not isinstance(record.id, models.NewId):
                # Exclude the record itself
                domain.append(("id", "!=", record.id))
            domain += [
                # Same speaker
                ("speaker_ids", "in", record.speaker_ids.ids),
                # Starts before this ends
                ("date", "<", record.date_end),
                # Ends after this starts
                ("date_end", ">", record.date),
            ]
            overlapping_tracks = EventTrack.search(domain)
            if overlapping_tracks:
                record.overlapping_speaker_track_ids = overlapping_tracks.ids
            else:
                record.overlapping_speaker_track_ids = False

    # 5. Constraints and onchanges

    # 6. CRUD methods
    def write(self, vals):
        res = super(EventTrack, self).write(vals)
        if vals.get("speaker_ids"):
            # TODO: Get ids correctly
            for speaker in vals.get("speaker_ids")[0][2]:
                self.message_subscribe([speaker])
        return res

    # 7. Action methods
    def _track_template(self, changes):
        res = super(EventTrack, self)._track_template(changes)
        track = self[0]
        if "stage_id" in changes and track.stage_id.mail_template_id:
            res["stage_id"] = (
                track.stage_id.mail_template_id,
                {
                    "composition_mode": "comment",
                    "subtype_id": self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_comment"
                    ),
                },
            )
        return res

    # 8. Business methods
