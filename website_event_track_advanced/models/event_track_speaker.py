from odoo import fields, models


class EventTrackSpeaker(models.Model):
    _name = "event.track.speaker"
    _order = "sequence"

    def _default_sequence(self):
        return (self.search([], order="sequence desc", limit=1).sequence or 0) + 1

    track_id = fields.Many2one(comodel_name="event.track", string="Track")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    email = fields.Char(related="partner_id.email")
    phone = fields.Char(related="partner_id.phone")
    sequence = fields.Integer(default=_default_sequence)
