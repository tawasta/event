from odoo import api, fields, models

class EventEvent(models.Model):
    _inherit = "event.event"

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        index=True,
        ondelete="set null",
    )
