from odoo import fields, models


class EventTrackSubtheme(models.Model):
    _name = "event.track.subtheme"
    _description = "Track Subtheme"

    name = fields.Char(string="Subtheme Name", required=True)
