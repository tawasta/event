from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventEvent(models.Model):
    _inherit = "event.event"

    allow_guest_registration = fields.Boolean(
        string="Allow registration without sign-in",
    )

    free_registration = fields.Boolean(
        string="Free registration",
        help="Helper field for showing if all tickets for this event are free",
        compute="_compute_free_registration",
    )

    @api.constrains("number")
    def check_allow_guest_registration(self):
        for record in self:
            if record.allow_guest_registration and not record.free_registration:
                raise ValidationError(
                    _("Guest registration can't be enabled if tickets aren't free")
                )

    def _compute_free_registration(self):
        for record in self:
            prices = record.event_ticket_ids.mapped("price")
            if sum(prices) == 0:
                record.free_registration = True
            else:
                record.free_registration = False
