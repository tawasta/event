from odoo import _, models


class EventTrack(models.Model):
    # 1. Private attributes
    _inherit = "event.track"

    def action_open_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Session Details"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }
