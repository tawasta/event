from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    registration_partner_category_ids = fields.Many2many(
        comodel_name="res.partner.category",
        relation="event_event_registration_partner_category_rel",
        column1="event_id",
        column2="category_id",
        string="Customer Tags",
        help="Tags added to the contact of each registration to this event. "
        "Existing tags of the contact are kept.",
    )
