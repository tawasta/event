import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    event_id = fields.Many2one(
        "event.event",
        string="Event",
        ondelete="cascade",
        help="Select an event for which the analytic distribution will be used "
        "(e.g. create new customer invoice or Sales order related to this event, "
        "it will automatically take this as an analytic account)",
    )

    event_ticket_id = fields.Many2one(
        "event.event.ticket",
        string="Event Ticket",
        ondelete="cascade",
        help="Select an ticket for which the analytic distribution will be used "
        "(e.g. create new customer invoice or Sales order related to this ticket, "
        "it will automatically take this as an analytic account)",
    )
