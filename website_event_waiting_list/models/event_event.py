from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventEvent(models.Model):
    # 1. Private attributes
    _inherit = "event.event"

    # 2. Fields declaration
    waiting_list = fields.Boolean(
        string="Enable Waiting List",
        compute="_compute_waiting_list",
        help="Enable waiting list when attendee limit is reached.",
        readonly=False,
        store=True,
    )
    seats_waiting = fields.Integer(
        string="Seats on waiting list",
        store=True,
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
        super(EventEvent, self)._compute_seats()

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

    @api.depends("event_type_id", "waiting_list")
    def _compute_waiting_list(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            event.waiting_list = event.event_type_id.waiting_list

    # @api.depends(
    #     "date_tz",
    #     "start_sale_datetime",
    #     "date_end",
    #     "seats_available",
    #     "seats_limited",
    #     "event_ticket_ids.sale_available",
    #     "stage_id",
    # )
    # def _compute_event_registrations_open(self):
    #     """Compute whether people may take registrations for this event
    #     * event.date_end -> if event is done, registrations are not open anymore;
    #     * event.
    #     * event.start_sale_datetime -> lowest start date of tickets (if any; start_sale_datetime
    #       is False if no ticket are defined, see _compute_start_sale_datetime);
    #     * any ticket is available for sale (seats available) if any;
    #     * seats are unlimited or seats are available;
    #     * allow registrations to waiting list if enabled
    #     """
    #     for event in self:
    #         event = event._set_tz_context()
    #         current_datetime = fields.Datetime.context_timestamp(
    #             event, fields.Datetime.now()
    #         )
    #         date_end_tz = (
    #             event.date_end.astimezone(pytz.timezone(event.date_tz or "UTC"))
    #             if event.date_end
    #             else False
    #         )
    #         event.event_registrations_open = (
    #             (
    #                 event.start_sale_datetime <= current_datetime.now()
    #                 if event.start_sale_datetime
    #                 else True
    #             )
    #             and (date_end_tz >= current_datetime if date_end_tz else True)
    #             and (
    #                 not event.seats_limited or event.seats_available
    #                 if not event.waiting_list
    #                 else True
    #             )
    #             and (
    #                 not event.event_ticket_ids
    #                 or any(ticket.sale_available for ticket in event.event_ticket_ids)
    #                 if not event.waiting_list
    #                 or all(ticket.is_expired for ticket in event.event_ticket_ids)
    #                 else True
    #             )
    #             and not event.stage_id.cancel
    #         )

    # 5. Constraints and onchanges
    @api.constrains("seats_limited", "waiting_list")
    def _check_waiting_list(self):
        """Turn off waiting list if seats are not limited"""
        for event in self:
            if event.waiting_list and not event.seats_limited:
                event.waiting_list = False

    # def _compute_is_participating(self):
    #     """Heuristic
    #     * public, no visitor: not participating as we have no information;
    #     * public and visitor: check visitor is linked to a registration. As
    #       visitors are merged on the top parent, current visitor check is
    #       sufficient even for successive visits;
    #     * logged, no visitor: check partner is linked to a registration. Do
    #       not check the email as it is not really secure;
    #     * logged as visitor: check partner or visitor are linked to a
    #       registration;
    #     """
    #     current_visitor = self.env["website.visitor"]._get_visitor_from_request(
    #         force_create=False
    #     )
    #     if self.env.user._is_public() and not current_visitor:
    #         events = self.env["event.event"]
    #     elif self.env.user._is_public():
    #         events = (
    #             self.env["event.registration"]
    #             .sudo()
    #             .search(
    #                 [
    #                     ("event_id", "in", self.ids),
    #                     ("state", "!=", "cancel"),
    #                     ("state", "!=", "wait"),
    #                     ("visitor_id", "=", current_visitor.id),
    #                 ]
    #             )
    #             .event_id
    #         )
    #     else:
    #         if current_visitor:
    #             domain = [
    #                 "|",
    #                 ("partner_id", "=", self.env.user.partner_id.id),
    #                 ("visitor_id", "=", current_visitor.id),
    #             ]
    #         else:
    #             domain = [("partner_id", "=", self.env.user.partner_id.id)]
    #         events = (
    #             self.env["event.registration"]
    #             .sudo()
    #             .search(
    #                 expression.AND(
    #                     [
    #                         domain,
    #                         [
    #                             "&",
    #                             ("event_id", "in", self.ids),
    #                             ("state", "!=", "cancel"),
    #                             ("state", "!=", "wait"),
    #                         ],
    #                     ]
    #                 )
    #             )
    #             .event_id
    #         )

    #     for event in self:
    #         event.is_participating = event in events

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods
    # def mail_attendees(
    #     self,
    #     template_id,
    #     force_send=False,
    #     filter_func=lambda self: self.state not in ["cancel", "wait", "draft"],
    # ):
    #     for event in self:
    #         for attendee in event.registration_ids.filtered(filter_func):
    #             self.env["mail.template"].browse(template_id).send_mail(
    #                 attendee.id, force_send=force_send
    #             )

    # 8. Business methods
