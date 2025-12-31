import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Event(models.Model):
    _name = "event.event"
    _inherit = ["event.event", "analytic.mixin"]

    matching_analytic_distribution_models_exist = fields.Boolean(
        compute="_compute_analytic_distribution_models_exist"
    )

    def _compute_analytic_distribution_models_exist(self):
        """
        Check if there are any analytic distributions that match this
        event and/or its tickets. Can be used to show an info message to the
        user accordingly.
        """

        analytic_distribution_model_obj = self.env[
            "account.analytic.distribution.model"
        ]
        for event in self:
            domain = [
                "|",
                ("event_id", "=", event.id),
                ("event_ticket_id", "in", event.event_ticket_ids.mapped("id")),
            ]

            matching_distributions = analytic_distribution_model_obj.sudo().search(
                domain=domain
            )

            event.matching_analytic_distribution_models_exist = (
                len(matching_distributions) > 0
            )
