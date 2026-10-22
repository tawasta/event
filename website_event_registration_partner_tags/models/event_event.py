from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    registration_partner_category_ids = fields.Many2many(
        comodel_name="res.company",
        string="Customer of",
        help="Companies added to the Customer of field of the contact of each "
        "registration to this event once the registration is confirmed. "
        "Existing companies of the contact are kept.",
    )
