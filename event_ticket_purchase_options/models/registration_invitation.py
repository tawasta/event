from odoo import fields, models


class RegistrationInvitation(models.Model):
    _name = "registration.invitation"
    _description = "Registration Invitation"

    registration_id = fields.Many2one(
        "event.registration", string="Registration", required=True
    )
    invite_email = fields.Char(string="Invite Email", required=True)
    invited_date = fields.Datetime(
        string="Invitation Date", default=fields.Datetime.now
    )
    is_used = fields.Boolean(string="Is Used", default=False)
    used_date = fields.Datetime(string="Used Date")
    access_token = fields.Char(
        string="Access Token", required=True, copy=False, index=True
    )
