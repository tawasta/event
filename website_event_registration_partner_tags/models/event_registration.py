from collections import defaultdict

from odoo import api, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.model_create_multi
    def create(self, vals_list):
        registrations = super().create(vals_list)
        registrations._add_event_partner_tags()
        return registrations

    def _add_event_partner_tags(self):
        """Add the event's customer tags that the registration contact lacks."""
        tags_by_partner = defaultdict(lambda: self.env["res.partner.category"])
        for registration in self.filtered("partner_id"):
            tags_by_partner[
                registration.partner_id
            ] |= registration.event_id.registration_partner_category_ids

        for partner, tags in tags_by_partner.items():
            missing_tags = tags - partner.category_id
            if missing_tags:
                # sudo: tagging is a side effect of registering, also for
                # website users and event users who cannot edit contacts
                partner.sudo().write(
                    {"category_id": [(4, tag.id) for tag in missing_tags]}
                )
