from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    restricted_mail_template_ids = fields.Many2many(
        related="website_id.restricted_mail_template_ids",
        comodel_name="mail.template",
        string="Rajoitetut Sähköpostipohjat",
        readonly=False,
    )

    blocked_states_ids = fields.Many2many(
        related="website_id.blocked_states_ids",
        comodel_name="event.stage",
        string="Blocked Event States",
        readonly=False,
    )


class Website(models.Model):
    _inherit = "website"

    restricted_mail_template_ids = fields.Many2many(
        comodel_name="mail.template",
        string="Rajoitetut Sähköpostipohjat",
    )

    blocked_states_ids = fields.Many2many(
        comodel_name="event.stage",
        string="Blocked Event States",
    )
