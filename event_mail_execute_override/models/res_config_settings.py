from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    restricted_mail_template_ids = fields.Many2many(
        related="website_id.restricted_mail_template_ids",
        comodel_name="mail.template",
        readonly=False,
    )


class Website(models.Model):
    _inherit = "website"

    restricted_mail_template_ids = fields.Many2many(
        comodel_name="mail.template",
        string="Restricted email templates",
        help="Don't send these email templates after an event has ended",
    )
