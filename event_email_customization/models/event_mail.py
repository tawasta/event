from odoo import models


class EventMail(models.Model):
    _inherit = "event.mail"

    def action_launch_email_template_preview(self):
        """
        Load Finnish as default when looking at event email previews
        """

        self.ensure_one()

        res = super().action_launch_email_template_preview()
        res["context"]["default_lang"] = "fi_FI"

        return res
