from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Marks lines created by splitting, so that they don't get split again, in
    # case user splits manually, and then post() would split again.
    event_ticket_line_split = fields.Boolean(copy=False)
