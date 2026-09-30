from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Marks lines created by splitting, so that they don't get split again, in
    # case user splits manually, and then post() would split again.
    event_ticket_line_split = fields.Boolean(copy=False)

    def _is_event_ticket_line(self):
        # Event ticket lines are event product lines that originate from an SO
        # line with an event, i.e. have registrations linked to them
        self.ensure_one()
        return bool(
            self.product_id.detailed_type == "event" and self.sale_line_ids.event_id
        )
