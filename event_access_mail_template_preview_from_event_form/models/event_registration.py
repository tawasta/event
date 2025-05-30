from odoo import models, fields, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    placeholder_for_email_preview = fields.Boolean(default=False)

    def action_unlink_placeholders(self):
        # Clean up any leftover records created for mail preview purposes

        placeholders_to_unlink = self.search(
            [("placeholder_for_email_preview", "=", True), ("state", "=", "draft")]
        )

        placeholders_to_unlink.unlink()
