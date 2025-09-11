from odoo import api, fields, models


class EventType(models.Model):
    _inherit = "event.type"

    registration_elsewhere = fields.Boolean(
        help="Selecting this option disables registration through the system "
        "and redirects registrations to an external link.",
        readonly=False,
        store=True,
    )
    registration_link = fields.Char(
        "Registration Link (URL)",
        help="Enter the URL address of an external registration link.",
        readonly=False,
        store=True,
    )


class EventEvent(models.Model):
    _inherit = "event.event"

    registration_elsewhere = fields.Boolean(
        help="Selecting this option disables registration through the system "
        "and redirects registrations to an external link.",
        readonly=False,
        store=True,
        compute="_compute_registration_elsewhere",
    )
    registration_link = fields.Char(
        "Registration Link (URL)",
        help="Enter the URL address of an external registration link.",
        readonly=False,
        store=True,
        compute="_compute_registration_link",
    )

    @api.depends("event_type_id")
    def _compute_registration_elsewhere(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if (
                event.event_type_id.registration_elsewhere
                != event.registration_elsewhere
            ):
                event.registration_elsewhere = (
                    event.event_type_id.registration_elsewhere
                )
            if not event.registration_elsewhere:
                event.registration_elsewhere = False

    @api.depends("event_type_id")
    def _compute_registration_link(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if not event.event_type_id:
                event.registration_link = event.registration_link or None
            else:
                event.registration_link = event.event_type_id.registration_link or None
