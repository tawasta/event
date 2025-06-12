from odoo import fields, models


class WaitingMailListMessage(models.TransientModel):
    # 1. Private attributes
    _name = "website.event.waiting.mail.list.message"
    _description = "Send message after mail action is sent"

    # 2. Fields declaration
    registration_ids = fields.Many2many("event.registration", string="Registrations")
    message = fields.Text(string="Confirm Waiting Message sent")

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
