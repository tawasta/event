from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    event_ids = fields.One2many(
        comodel_name="event.event",
        inverse_name="project_id",
        string="Events",
    )
    event_count = fields.Integer(
        compute="_compute_event_count",
    )

    def _compute_event_count(self):
        for project in self:
            project.event_count = len(project.event_ids)
