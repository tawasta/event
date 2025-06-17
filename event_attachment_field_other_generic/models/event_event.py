import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    other_generic_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Other Attachment",
        domain="[('res_model', '=', 'event.event')]",
        ondelete="cascade",
        help="Other generic attachment for this event. Copy the URL to link "
        "to the file in e.g. e-mail templates",
    )

    other_generic_attachment_url = fields.Char(
        string="Other Attachment URL",
        compute="_compute_other_generic_attachment_url",
        store=True,
    )

    @api.depends("other_generic_attachment_id")
    def _compute_other_generic_attachment_url(self):
        for event in self:
            attachment = event.other_generic_attachment_id
            if attachment and attachment.public:
                event.other_generic_attachment_url = (
                    f"/web/content/{attachment.id}?download=true"
                )
            else:
                event.other_generic_attachment_url = False
