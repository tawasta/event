from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    program_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Event Program",
        domain="[('res_model', '=', 'event.event')]",
        ondelete="cascade",
        help="Program for this event. Copy the URL to link to the file in e.g. "
        "e-mail templates",
    )

    program_attachment_url = fields.Char(
        string="Event Program URL",
        compute="_compute_program_attachment_url",
        store=True,
    )

    @api.depends("program_attachment_id")
    def _compute_program_attachment_url(self):
        for event in self:
            attachment = event.program_attachment_id
            if attachment and attachment.public:
                event.program_attachment_url = (
                    f"/web/content/{attachment.id}?download=true"
                )
            else:
                event.program_attachment_url = False
