import re

from odoo import api, fields, models


class EventTrackType(models.Model):
    _name = "event.track.type"
    _description = "Event Track Type"
    _order = "sequence, name"

    def _default_sequence(self):
        return (self.search([], order="sequence desc", limit=1).sequence or 0) + 1

    # 2. Fields declaration
    sequence = fields.Integer(default=_default_sequence)
    code = fields.Char(copy=False, translate=False, required=True)
    name = fields.Char(translate=True, required=True)
    description = fields.Text(translate=True)
    active = fields.Boolean(default=True)
    event_tracks = fields.One2many(
        comodel_name="event.track", inverse_name="type", string="Event Track"
    )
    show_in_proposals = fields.Boolean(help="Show in proposals form", default=True)
    show_in_agenda = fields.Boolean(help="Show in website agenda", default=True)
    attendable = fields.Boolean(
        help="If the presentation type can be attended. "
        "Unattendable types will be muted in the agenda",
        default=True,
    )
    twitter_hashtag = fields.Char(string="X hashtag", help="X hashtag for tracks")
    workshop = fields.Boolean(
        help="Tracks in this Type can hold workshops", default=False
    )
    workshop_contract = fields.Boolean(
        help="Tracks in this type require signing a workshop contract",
        default=False,
    )
    webinar = fields.Boolean(help="Tracks in this type can hold webinars", default=True)

    privacy_id = fields.Many2one(
        "privacy.activity",
        string="Privacies",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    _sql_constraints = [("code", "unique(code)", "Please use an unique code")]

    @api.onchange("twitter_hashtag")
    def onchange_twitter_hashtag_sanitize(self):
        for record in self:
            if record.twitter_hashtag:
                hashtag = re.sub("[^A-Za-z0-9_]", "", record.twitter_hashtag)
                record.twitter_hashtag = hashtag
