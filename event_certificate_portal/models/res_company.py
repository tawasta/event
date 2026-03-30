from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    event_certificate_signature = fields.Image(
        string="Event certificate signature",
        max_width=1024,
        max_height=1024,
    )
    event_certificate_signatory_name = fields.Char(
        string="Certificate signatory name",
    )
    event_certificate_signatory_title = fields.Char(
        string="Certificate signatory title",
    )
