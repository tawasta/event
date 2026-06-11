from odoo import api, models


class EventType(models.Model):
    _inherit = "event.type"

    @api.model
    def _default_event_mail_type_ids(self):
        """Use custom templates for all event communications.

        Replaces core reminders (1 week + 1 day before) and waiting list
        templates with our own versions.
        """
        return [
            # Immediate registration confirmation
            (
                0,
                0,
                {
                    "notification_type": "mail",
                    "interval_nbr": 0,
                    "interval_unit": "now",
                    "interval_type": "after_sub",
                    "template_ref": "mail.template,%i"
                    % self.env.ref(
                        "event_email_customization.event_registration_custom"
                    ).id,
                },
            ),
            # 1 week before event reminder
            (
                0,
                0,
                {
                    "notification_type": "mail",
                    "interval_nbr": 7,
                    "interval_unit": "days",
                    "interval_type": "before_event",
                    "template_ref": "mail.template,%i"
                    % self.env.ref(
                        "event_email_customization.event_reminder_custom_7d"
                    ).id,
                },
            ),
            # 1 day before event reminder
            (
                0,
                0,
                {
                    "notification_type": "mail",
                    "interval_nbr": 1,
                    "interval_unit": "days",
                    "interval_type": "before_event",
                    "template_ref": "mail.template,%i"
                    % self.env.ref(
                        "event_email_customization.event_reminder_custom_1d"
                    ).id,
                },
            ),
            # Waiting list confirmation
            (
                0,
                0,
                {
                    "notification_type": "mail",
                    "interval_nbr": 0,
                    "interval_unit": "now",
                    "interval_type": "after_wait",
                    "template_ref": "mail.template,%i"
                    % self.env.ref("event_email_customization.event_waiting_custom").id,
                },
            ),
            # Waiting list open seats notification
            (
                0,
                0,
                {
                    "notification_type": "mail",
                    "interval_nbr": 0,
                    "interval_unit": "now",
                    "interval_type": "after_seats_available",
                    "template_ref": "mail.template,%i"
                    % self.env.ref(
                        "event_email_customization.event_confirm_waiting_custom"
                    ).id,
                },
            ),
        ]
