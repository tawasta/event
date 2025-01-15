from odoo import api, fields, models
from odoo.tools.misc import formatLang
from odoo.tools.translate import _
import logging

class EventEvent(models.Model):
    _inherit = 'event.event'


    @api.depends('name', 'date_begin', 'date_end', 'event_registrations_sold_out', 'seats_limited', 'seats_max', 'seats_available')
    @api.depends_context('name_with_seats_availability')
    def _compute_display_name(self):
        """
        Compute the display name to include event name, date range, and seat availability if required.
        """
        for event in self:
            name = event.name or ""

            # Add seat availability if requested
            if self.env.context.get('name_with_seats_availability'):
                if event.event_registrations_sold_out:
                    name = _('%(event_name)s (Sold out)', event_name=name)
                elif event.seats_limited and event.seats_max:
                    name = _(
                        '%(event_name)s (%(count)s seats remaining)',
                        event_name=name,
                        count=formatLang(self.env, event.seats_available, digits=0),
                    )

            # Append date range if available
            if event.date_begin:
                dates = []
                dates.append(fields.Date.to_string(fields.Datetime.context_timestamp(event, fields.Datetime.from_string(event.date_begin))))
                name += ' (%s)' % ' - '.join(dates)

            event.display_name = name
