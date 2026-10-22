from collections import defaultdict

from odoo import models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def write(self, vals):
        res = super().write(vals)
        # Every confirmation ends here: auto confirmation on create, a free
        # sale order being confirmed and a paid invoice all call action_confirm
        if vals.get("state") == "open":
            self._add_event_partner_tags()
        return res

    def _add_event_partner_tags(self):
        """Add the event's companies that the registration contact lacks as
        customer of."""
        companies_by_partner = defaultdict(lambda: self.env["res.company"])
        for registration in self.filtered("partner_id"):
            companies_by_partner[
                registration.partner_id
            ] |= registration.event_id.registration_partner_category_ids

        for partner, companies in companies_by_partner.items():
            missing_companies = companies - partner.customer_of
            if missing_companies:
                # sudo: this is a side effect of registering, also for
                # website users and event users who cannot edit contacts
                partner.sudo().write(
                    {"customer_of": [(4, company.id) for company in missing_companies]}
                )
