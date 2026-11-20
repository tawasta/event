from odoo import fields, models
from odoo.tools import is_html_empty


class Website(models.Model):
    _inherit = "website"

    event_registration_self_help = fields.Html(
        string="Help for Registering Only Myself",
        translate=True,
        sanitize=True,
    )
    event_registration_others_help = fields.Html(
        string="Help for Registering Other Participants",
        translate=True,
        sanitize=True,
    )

    def _get_event_registration_help(self):
        """Return the registration option help texts that have content.

        The HTML editor stores an emptied field as markup such as
        ``<p><br></p>``, so a plain truthiness check is not enough.
        """
        self.ensure_one()
        help_texts = {
            "self": self.event_registration_self_help,
            "others": self.event_registration_others_help,
        }
        return {
            option: text
            for option, text in help_texts.items()
            if not is_html_empty(text)
        }
