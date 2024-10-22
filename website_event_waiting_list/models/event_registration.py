from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventRegistration(models.Model):

    # 1. Private attributes
    _inherit = "event.registration"

    # 2. Fields declaration
    waiting_list = fields.Boolean(related="event_id.waiting_list", store=True)
    waiting_list_to_confirm = fields.Boolean(
        string="Available to confirm from waiting list",
        readonly=True,
        compute_sudo=True,
        compute="_compute_available_to_confirm",
    )
    state = fields.Selection(selection_add=[("wait", "Waiting")])

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.depends("event_id.seats_available")
    def _compute_available_to_confirm(self):
        """
        Compute all cases where registration from waiting list can be confirmed:
        1. Both ticket and event have limited but available seats
        2. Both ticket and event have no limited seats
        3. Ticket has no limited seats and event has limited but available seats
        4. Ticket has limited but available seats and event has no limited seats
        5. No ticket used and event has available seats
        """
        for registration in self:
            if (
                registration.waiting_list
                and registration.state == "wait"
                and (
                    (
                        not registration.event_id.seats_limited
                        or not registration.event_id.seats_max
                    )
                    or (
                        registration.event_id.seats_available > 0
                        and registration.event_id.seats_limited
                        and registration.event_id.seats_max
                    )
                )
                and (
                    (
                        not registration.event_ticket_id
                        or not registration.event_ticket_id.seats_limited
                        or not registration.event_ticket_id.seats_max
                    )
                    or (
                        registration.event_ticket_id.seats_available > 0
                        and registration.event_ticket_id.seats_limited
                        and registration.event_ticket_id.seats_max
                    )
                )
            ):
                registration.waiting_list_to_confirm = True
            else:
                registration.waiting_list_to_confirm = False

    def _compute_confirm_url(self):
        """Url to confirm registration (move state from wait -> open)"""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for registration in self:
            registration.confirm_url = urls.url_join(
                base_url,
                "/event/%s/waiting-list/confirm/%s"
                % (registration.event_id.id, registration.access_token),
            )

    # 5. Constraints and onchanges
    # @api.constrains("event_id", "state")
    # def _check_seats_limit(self):
    #     """
    #     Raise validation error if no waiting list and seats are full
    #     Or if seats are full and trying to confirm a registration
    #     """
    #     for registration in self:
    #         for registration in self:
    #             if (
    #                 registration.event_id.seats_limited
    #                 and registration.event_id.seats_max
    #                 and registration.event_id.seats_available
    #                 < (1 if registration.state == "draft" else 0)
    #             ):
    #                 if not registration.event_id.waiting_list:
    #                     raise ValidationError(
    #                         _("No more seats available for this event.")
    #                     )
    #                 if (
    #                     registration.event_id.waiting_list
    #                     and registration.state not in ["draft", "wait"]
    #                 ):
    #                     raise ValidationError(
    #                         _("No more seats available for this event.")
    #                     )

    # @api.constrains("event_ticket_id", "state")
    # def _check_ticket_seats_limit(self):
    #     """
    #     Raise validation error if no waiting list and seats are full
    #     Or if seats are full and trying to confirm a registration
    #     """
    #     for registration in self:
    #         if (
    #             registration.event_ticket_id.seats_max
    #             and registration.event_ticket_id.seats_available < 0
    #         ):
    #             if not registration.event_ticket_id.waiting_list:
    #                 raise ValidationError(_("No more seats available for this ticket."))
    #             if (
    #                 registration.event_ticket_id.waiting_list
    #                 and registration.state not in ["draft", "wait"]
    #             ):
    #                 raise ValidationError(_("No more seats available for this ticket."))

    # 6. CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to assign correct state. Includes 3 cases.
        1. Auto confirm when available seats and auto confirm enabled
        2. Add to waiting list when no available seats and waiting list enabled
        3. Add registration as draft otherwise
        """
        # pass context to skip auto_confirm on super method
        add_waiting_list = False
        for vals in vals_list:
            if self._check_waiting_list(vals):
                add_waiting_list = True

        registrations = super(EventRegistration, self).create(vals_list)
        registrations = registrations.with_context(skip_confirm_wait=False)
        # if registrations._check_auto_confirmation():
        #     registrations.sudo().action_confirm()
        if add_waiting_list:
            registrations.sudo().action_waiting()
        return registrations

    def write(self, vals):
        """Auto-trigger mail schedulers on state writes"""
        res = super().write(vals)

        for rec in self:

            event_stage = rec.event_id.stage_id
            if event_stage.pipe_end or event_stage.cancel:
                # Don't try to send messages for closed events
                return res

            if vals.get("state") == "open":
                onsubscribe_schedulers = rec.mapped("event_id.event_mail_ids").filtered(
                    lambda s: s.interval_type == "after_sub"
                )
                onsubscribe_schedulers.sudo().execute()
            if vals.get("state") == "wait":
                onsubscribe_schedulers = rec.mapped("event_id.event_mail_ids").filtered(
                    lambda s: s.interval_type == "after_wait"
                )
                onsubscribe_schedulers.sudo().execute()
        return res

    # 7. Action methods
    def action_waiting(self):
        if not self.event_id.waiting_list:
            raise ValidationError(_("Waiting list for this event is not enabled."))
        self.write({"state": "wait"})

    def _check_waiting_list(self, vals):
        event = self.env["event.event"].browse(vals["event_id"])
        event_ticket = self.env["event.event.ticket"]

        if not vals.get("event_ticket_id"):
            return False  # Ei lisätä jonotuslistalle
        ticket = (
            event_ticket.browse(vals["event_ticket_id"])
            if vals.get("event_ticket_id")
            else event_ticket
        )
        if (
            event.waiting_list  # Jonotuslista on käytössä
            and event.seats_limited  # Tapahtumalla on rajattu määrä paikkoja
            and event.seats_available <= 0  # Paikkoja ei ole jäljellä
            and ticket.seats_limited  # Lipuilla on rajattu määrä paikkoja
            and ticket.seats_available <= 0  # Lippuja ei ole jäljellä
        ):
            return True  # Lisätään jonotuslistalle
        else:
            return False  # Ei lisätä jonotuslistalle

        # for registration in self:
        #     if (not registration.event_id.waiting_list) or (
        #         registration.event_id.seats_limited
        #         and registration.event_id.seats_available > 0
        #         and (
        #             not registration.event_ticket_id.seats_limited
        #             or registration.event_ticket_id.seats_available > 0
        #         )
        #     ):
        #         return False
        #     return True

    # def _check_auto_confirmation(self):
    #     if self._context.get("skip_confirm") or self._context.get("skip_confirm_wait"):
    #         return False
    #     if any(
    #         not registration.event_id.auto_confirm
    #         or (
    #             registration.event_id.seats_available <= 0
    #             and registration.event_id.seats_limited
    #             or registration.event_ticket_id.seats_available <= 0
    #             and registration.event_ticket_id.seats_limited
    #         )
    #         for registration in self
    #     ):
    #         return False
    #     return True

    # 8. Business methods
