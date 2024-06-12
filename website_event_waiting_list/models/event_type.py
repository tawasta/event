from odoo import api, fields, models


class EventType(models.Model):
    # 1. Private attributes
    _inherit = "event.type"

    # 2. Fields declaration
    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        help="Enable waiting list when attendee limit is reached.",
        default=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("use_mail_schedule")
    def _compute_event_type_mail_ids(self):
        for template in self:
            if not template.use_mail_schedule:
                template.event_type_mail_ids = [(5, 0)]
            elif not template.event_type_mail_ids:
                template.event_type_mail_ids = [
                    (
                        0,
                        0,
                        {
                            "notification_type": "mail",
                            "interval_unit": "now",
                            "interval_type": "after_sub",
                            "template_id": self.env.ref("event.event_subscription").id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "notification_type": "mail",
                            "interval_nbr": 10,
                            "interval_unit": "days",
                            "interval_type": "before_event",
                            "template_id": self.env.ref("event.event_reminder").id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "notification_type": "mail",
                            "interval_unit": "now",
                            "interval_type": "after_wait",
                            "template_id": self.env.ref(
                                "website_event_waiting_list.event_waiting"
                            ).id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "notification_type": "mail",
                            "interval_unit": "now",
                            "interval_type": "after_seats_available",
                            "template_id": self.env.ref(
                                "website_event_waiting_list.event_confirm_waiting_registration"
                            ).id,
                        },
                    ),
                ]

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
