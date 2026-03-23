import uuid

from werkzeug import urls

from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    manage_url = fields.Char("Public link", compute="_compute_manage_url")
    access_token = fields.Char(
        "Security Token", readonly=True, default=lambda self: str(uuid.uuid4())
    )

    @api.depends("event_id", "access_token")
    def _compute_manage_url(self):
        """Url to cancel registration"""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for registration in self:
            registration.manage_url = urls.url_join(
                base_url,
                f"/event/{registration.event_id.id}/registration/manage/{registration.access_token}",
            )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to assign write access_token.
        """
        registrations = super().create(vals_list)
        registrations = registrations.with_context(skip_confirm=False)
        return registrations

    def _check_auto_confirmation(self):
        if self._context.get("skip_confirm"):
            return False
        if any(
            not registration.event_id.auto_confirm
            or (
                not registration.event_id.seats_available
                and registration.event_id.seats_limited
            )
            for registration in self
        ):
            return False
        return True
