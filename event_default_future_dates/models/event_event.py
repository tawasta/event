from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    @api.model
    def _get_default_dates_offset(self):
        """How far into the future new and duplicated events are placed, fetch
        from config parameters, fall back to 1 months if necessary.
        """

        default_offset_months = 1

        months = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "event_default_future_dates.months", default=default_offset_months
            )
        )

        try:
            months = int(months)
        except (TypeError, ValueError):
            months = default_offset_months

        return relativedelta(months=months)

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)

        # An explicitly requested date wins, e.g. when creating an event by
        # clicking a slot in the calendar view
        if self.env.context.get("default_date_begin"):
            return result

        if result.get("date_begin"):
            # Replace the core's date_begin with one further on in the future
            date_begin_original = fields.Datetime.to_datetime(result["date_begin"])
            result["date_begin"] = (
                date_begin_original + self._get_default_dates_offset()
            )

            if result.get("date_end"):
                # Keep the duration core came up with
                date_end_original = fields.Datetime.to_datetime(result["date_end"])
                duration = date_end_original - date_begin_original
                result["date_end"] = result["date_begin"] + duration

        return result

    def copy(self, default=None):
        self.ensure_one()

        default = dict(default or {})

        # A caller asking for specific dates still gets them
        dates_should_default = (
            self.date_begin
            and self.date_end
            and "date_begin" not in default
            and "date_end" not in default
        )

        if dates_should_default:
            duration = self.date_end - self.date_begin
            now = fields.Datetime.now()
            new_date_begin = (
                now.replace(second=0, microsecond=0)
                + timedelta(minutes=-now.minute % 30)
                + self._get_default_dates_offset()
            )
            default["date_begin"] = new_date_begin
            default["date_end"] = new_date_begin + duration

        event = super().copy(default)

        if dates_should_default:
            event.message_post(
                body=_(
                    "While copying, the dates of this event were set to a "
                    "placeholder date in the future."
                )
            )

        return event
