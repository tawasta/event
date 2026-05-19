from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    certificate_enabled = fields.Boolean(
        string="Certificates enabled",
        help="Enable attendance certificates for this event.",
        tracking=True,
    )
    certificate_send_email = fields.Boolean(
        string="Send certificate by email after event",
        help=(
            "If enabled, attended registrations receive the certificate "
            "automatically after the event."
        ),
        tracking=True,
    )
    certificate_duration_text = fields.Char(
        string="Certificate duration",
        help="Free text shown on the certificate, for example: 2 x 45 min",
    )
    certificate_lecturer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lecturer on certificate",
        help="Lecturer shown on the attendance certificate.",
    )

    certificate_program_text = fields.Text(
        string="Training programme on certificate",
        help="Multiline programme text shown on the attendance certificate.",
        tracking=True,
    )

    certificate_lang = fields.Selection(
        selection=lambda self: self.env["res.lang"].get_installed(),
        string="Certificate language",
        default=lambda self: self.env.lang,
        help="Language used when printing the attendance certificate.",
        tracking=True,
    )
