import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    invite_others = fields.Boolean(
        default=False,
    )

    invite_id = fields.Many2one(
        string="Invitation", comodel_name="registration.invitation"
    )
