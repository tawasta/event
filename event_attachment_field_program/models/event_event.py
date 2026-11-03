import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    program_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Event Program",
        domain="[('res_model', '=', 'event.event')]",
        ondelete="set null",
        copy=False,
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

    @api.model
    def _get_linked_attachment_fields(self):
        return super()._get_linked_attachment_fields() + ["program_attachment_id"]
