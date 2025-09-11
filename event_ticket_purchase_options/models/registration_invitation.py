from odoo import fields, models


class RegistrationInvitation(models.Model):
    _name = "registration.invitation"
    _description = "Registration Invitation"
    _rec_name = "invite_email"

    registration_id = fields.Many2one(
        "event.registration", string="Registration", required=True
    )
    invite_email = fields.Char(required=True)
    invited_date = fields.Datetime(
        string="Invitation Date", default=fields.Datetime.now
    )
    is_used = fields.Boolean(default=False)
    used_date = fields.Datetime()
    access_token = fields.Char(required=True, copy=False, index=True)
