import uuid

from werkzeug import urls

from odoo import api, fields, models


class EventRegistration(models.Model):
    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
    manage_url = fields.Char("Public link", compute="_compute_manage_url")
    access_token = fields.Char(
        "Security Token", readonly=True, default=lambda self: str(uuid.uuid4())
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_id", "access_token")
    def _compute_manage_url(self):
        """Url to cancel registration"""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for registration in self:
            registration.manage_url = urls.url_join(
                base_url,
                "/event/{}/registration/manage/{}".format(
                    registration.event_id.id, registration.access_token
                ),
            )

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to assign write access_token.
        """
        registrations = super().create(vals_list)
        registrations = registrations.with_context(skip_confirm=False)
        return registrations

    # 7. Action methods
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

    # 8. Business methods
