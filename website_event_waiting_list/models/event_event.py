from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        help="Enable waiting list when attendee limit is reached.",
        tracking=True,
    )
    seats_waiting = fields.Integer(
        string="Seats on waiting list",
        readonly=True,
        compute="_compute_seats",
    )

    # 3. Default methods

    @api.constrains("seats_max", "seats_limited", "registration_ids")
    def _check_seats_availability(self, minimal_availability=0):
        sold_out_events = []
        for event in self:
            if (
                not event.waiting_list
                and event.seats_limited
                and event.seats_max
                and event.seats_available < minimal_availability
            ):
                sold_out_events.append(
                    _(
                        '- "%(event_name)s": Missing %(nb_too_many)i seats.',
                        event_name=event.name,
                        nb_too_many=-event.seats_available,
                    )
                )
        if sold_out_events:
            raise ValidationError(
                _("There are not enough seats available for:")
                + "\n%s\n" % "\n".join(sold_out_events)
            )

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("seats_max", "registration_ids.state", "registration_ids.active")
    def _compute_seats(self):
        """Extend the original _compute_seats method to account for waiting list."""
        super()._compute_seats()

        # Add logic for waiting list
        for event in self:
            event.seats_waiting = 0

        state_field = {"wait": "seats_waiting"}

        base_vals = {fname: 0 for fname in state_field.values()}
        results = {event_id: dict(base_vals) for event_id in self.ids}

        if self.ids:
            query = """ SELECT event_id, state, count(event_id)
                        FROM event_registration
                        WHERE event_id IN %s AND state = 'wait' AND active = true
                        GROUP BY event_id, state
                    """
            self.env["event.registration"].flush_model(["event_id", "state", "active"])
            self._cr.execute(query, (tuple(self.ids),))
            res = self._cr.fetchall()
            for event_id, state, num in res:
                results[event_id][state_field[state]] = num

        for event in self:
            event.update(results.get(event._origin.id or event.id, base_vals))

            if event.waiting_list and event.seats_available > 0:
                onsubscribe_schedulers = event.event_mail_ids.filtered(
                    lambda s: s.interval_type == "after_seats_available"
                )
                onsubscribe_schedulers.sudo().execute()
                # Mark mails as not sent if seats become unavailable again
                registrations_to_not_sent = event.event_mail_ids.mapped(
                    "mail_registration_ids"
                ).filtered(
                    lambda reg_mail: reg_mail.mail_sent
                    and reg_mail.registration_id.state == "wait"
                    and reg_mail.scheduler_id.notification_type == "mail"
                    and reg_mail.scheduler_id.interval_type == "after_seats_available"
                    and not reg_mail.registration_id.waiting_list_to_confirm
                )
                registrations_to_not_sent.write({"mail_sent": False})

    @api.onchange("event_type_id")
    def _onchange_event_type_update_wait_list(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its subfields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if event.event_type_id:
                event.waiting_list = event.event_type_id.waiting_list

    # 5. Constraints and onchanges
    @api.constrains("seats_limited", "waiting_list")
    def _check_waiting_list(self):
        """Turn off waiting list if seats are not limited"""
        for event in self:
            if event.waiting_list and not event.seats_limited:
                event.waiting_list = False

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
