import base64
import io
import logging

import qrcode

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    qr_code = fields.Binary(
        string="QR Code",
        compute="_compute_qr_code",
        store=True,
        readonly=True,
    )

    @api.depends("feedback_survey_id", "survey_start_url")
    def _compute_qr_code(self):
        for record in self:
            # Näytetään QR vain jos palaute-kysely on kytketty ja url on olemassa
            if record.feedback_survey_id and record.survey_start_url:
                try:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=8,  # 20 on todella suuri; 6–10 toimii yleensä paremmin
                        border=2,
                    )
                    qr.add_data(record.survey_start_url)
                    qr.make(fit=True)
                    img = qr.make_image()  # Pillow image

                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    record.qr_code = base64.b64encode(buf.getvalue())
                except Exception as e:
                    _logger.exception(
                        "QR code generation failed for event %s: %s", record.id, e
                    )
                    record.qr_code = False
            else:
                record.qr_code = False
