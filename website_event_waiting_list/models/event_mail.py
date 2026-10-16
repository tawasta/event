##############################################################################
#
#    Author: Futural Oy
#    Copyright 2021- Futural Oy (https://futural.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Mail template of each waiting-list scheduler type
WAITING_LIST_MAIL_TEMPLATES = {
    "after_wait": "website_event_waiting_list.event_waiting",
    "after_seats_available": (
        "website_event_waiting_list.event_confirm_waiting_registration"
    ),
}
WAITING_LIST_INTERVAL_TYPES = tuple(WAITING_LIST_MAIL_TEMPLATES)
WAITING_LIST_INTERVAL_SELECTION = [
    ("after_wait", "After registering to waiting list"),
    (
        "after_seats_available",
        "After more seats are available send to waiting list registrations",
    ),
]
WAITING_LIST_INTERVAL_ONDELETE = dict.fromkeys(WAITING_LIST_INTERVAL_TYPES, "cascade")


class EventMailScheduler(models.Model):
    _inherit = "event.mail"

    interval_type = fields.Selection(
        selection_add=WAITING_LIST_INTERVAL_SELECTION,
        ondelete=WAITING_LIST_INTERVAL_ONDELETE,
    )

    @api.model
    def _get_waiting_list_templates(self):
        """Mail template of each waiting-list scheduler type.

        A deleted template is skipped instead of raising, as that must not block
        creating an event or an event template.
        """
        return {
            interval_type: template
            for interval_type, xmlid in WAITING_LIST_MAIL_TEMPLATES.items()
            if (template := self.env.ref(xmlid, raise_if_not_found=False))
        }

    def execute(self):
        """Run the waiting-list schedulers here, the others in core.

        Core has no branch for them and would mail everyone. "after_wait" is sent
        when someone joins (see :meth:`_trigger_immediate_mail`),
        "after_seats_available" is run by the cron of core.
        """
        self.filtered(
            lambda scheduler: scheduler.interval_type == "after_seats_available"
        )._notify_waiting_list()
        return super(
            EventMailScheduler,
            self.filtered(lambda s: s.interval_type not in WAITING_LIST_INTERVAL_TYPES),
        ).execute()

    def _notify_waiting_list(self):
        """Mail the waiting registrations that can be confirmed now.

        Resets ``mail_sent`` of those that cannot any more (the seat was taken
        before they confirmed), so a later round notifies them again. Nothing is
        left to do once the event is over.
        """
        for scheduler in self:
            event = scheduler.event_id
            if event.date_end < fields.Datetime.now():
                scheduler.mail_done = True
                continue
            waiting = self.env["event.registration"].search(
                [("event_id", "=", event.id), ("state", "=", "wait")]
            )
            eligible = waiting.filtered("waiting_list_to_confirm")
            scheduler._trigger_immediate_mail(eligible)
            scheduler._reset_notified(waiting - eligible)

    def _execute_event_based_for_registrations(self, registrations):
        """Event-wide mails (reminders, thanks) are not for the waiting list.

        Core selects every registration that is not cancelled or draft, and the
        waiting ones have no place at the event.
        """
        return super()._execute_event_based_for_registrations(
            registrations.filtered(lambda registration: registration.state != "wait")
        )

    def _trigger_immediate_mail(self, registrations):
        """Send these schedulers' mail to ``registrations`` right away.

        Also to one whose ``mail_sent`` was reset, not only to new ones. A failing
        mail must not break the registration or the confirmation that triggered
        it, so the error is reported on the event like core does.
        """
        if not registrations:
            return
        for scheduler in self:
            try:
                with self.env.cr.savepoint():
                    scheduler._get_or_create_mail_registrations(registrations).filtered(
                        lambda mail_reg: not mail_reg.mail_sent
                    )._execute_on_registrations()
            except Exception as exc:  # noqa: BLE001
                _logger.exception("Failed to run scheduler %s", scheduler.id)
                scheduler._warn_error(exc)

    def _get_mail_registrations(self, registrations):
        """The mails of these schedulers to these registrations."""
        return self.env["event.mail.registration"].search(
            [
                ("scheduler_id", "in", self.ids),
                ("registration_id", "in", registrations.ids),
            ]
        )

    def _get_or_create_mail_registrations(self, registrations):
        self.ensure_one()
        tracked = self._get_mail_registrations(registrations)
        return tracked | self._create_missing_mail_registrations(
            registrations - tracked.registration_id
        )

    def _reset_notified(self, registrations):
        """Make the mails to these registrations go out again at the next chance."""
        self._get_mail_registrations(registrations).filtered("mail_sent").write(
            {"mail_sent": False}
        )

    def _mark_mail_sent(self, registrations):
        """Record the mails to ``registrations`` as sent, e.g. when sent by hand."""
        for scheduler in self:
            scheduler._get_or_create_mail_registrations(registrations).write(
                {"mail_sent": True}
            )

    def _create_missing_mail_registrations(self, registrations):
        """Do not queue the "after subscription" mails of the waiting list.

        Core queues them for every registration that is not cancelled or draft.
        The waiting ones get them when they are confirmed.
        """
        regular = self.filtered(
            lambda scheduler: scheduler.interval_type not in WAITING_LIST_INTERVAL_TYPES
        )
        new = super(EventMailScheduler, regular)._create_missing_mail_registrations(
            registrations.filtered(lambda registration: registration.state != "wait")
        )
        return new | super(
            EventMailScheduler, self - regular
        )._create_missing_mail_registrations(registrations)

    @api.depends("interval_type")
    def _compute_scheduled_date(self):
        """The scheduler of the free seats runs from the start, the join mail never.

        Core would give both the end of the event as the date, so the cron would
        not run the first before it, and would keep the second for ever.
        """
        res = super()._compute_scheduled_date()
        for scheduler in self:
            if scheduler.interval_type == "after_seats_available":
                scheduler.scheduled_date = fields.Datetime.now()
            elif scheduler.interval_type == "after_wait":
                scheduler.scheduled_date = False
        return res


class EventMailRegistration(models.Model):
    _inherit = "event.mail.registration"

    def _get_skip_domain(self):
        """Do not send the "after subscription" mails to the waiting list.

        They stay pending and go out when the registration is confirmed.
        """
        return super()._get_skip_domain() + [("registration_id.state", "!=", "wait")]
