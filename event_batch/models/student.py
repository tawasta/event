from odoo import fields, models


class OpStudent(models.Model):
    _inherit = "op.student"

    event_count = fields.Integer(
        "# Events",
        compute="_compute_event_count",
        help="Number of events the partner has participated.",
    )

    def _compute_event_count(self):
        self.event_count = 0

        for student in self:
            student.event_count = self.env["event.event"].search_count(
                [
                    (
                        "registration_ids.attendee_partner_id",
                        "child_of",
                        student.partner_id.ids,
                    )
                ]
            )

    def action_event_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("event.action_event_view")
        action["context"] = {}
        action["domain"] = [
            ("registration_ids.attendee_partner_id", "child_of", self.partner_id.ids)
        ]
        return action
