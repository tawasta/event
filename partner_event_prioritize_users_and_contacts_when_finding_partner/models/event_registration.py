import logging

from odoo import models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def _find_best_matching_partner(self, email):
        """Find the best matching partner for a given email address.

        When multiple partners share the same email, apply the following
        priority order:
          1. A partner that has a linked user account (user_ids is set)
          2. A contact partner (is_company=False)
          3. Any partner (fallback, including companies. Equivalent to
             partner_event module's logic)

        Returns a single res.partner record (or empty recordset).
        """

        Partner = self.env["res.partner"]
        candidates = Partner.search([("email", "=ilike", email)], order="id")
        if len(candidates) <= 1:
            return candidates

        _logger.info(
            "Multiple partners (%d) found for email '%s', applying priority",
            len(candidates),
            email,
        )

        # Priority 1: Partner with a linked user account
        with_user = candidates.filtered(lambda p: p.user_ids)
        if with_user:
            _logger.info(
                "P1: Selected partner %s (ID %d) — has user account",
                with_user[0].name,
                with_user[0].id,
            )
            return with_user[0]

        # Priority 2: A contact (not a company)
        contacts = candidates.filtered(lambda p: not p.is_company)
        if contacts:
            _logger.info(
                "P2: Selected partner %s (ID %d) — is a contact",
                contacts[0].name,
                contacts[0].id,
            )
            return contacts[0]

        # Priority 3: Fallback to first by ID
        _logger.info(
            "P3: Selected partner %s (ID %d) — fallback, first by ID",
            candidates[0].name,
            candidates[0].id,
        )
        return candidates[0]

    def _update_attendee_partner_id(self, vals):
        # Replace the partner_event function: otherwise the same functionality, but
        # _find_best_matching_partner() call replaces the simple search() call
        # of the OCA module.

        if (
            not vals.get("attendee_partner_id")
            and vals.get("email")
            and not self.env.context.get("partner_event_merging")
        ):
            Partner = self.env["res.partner"]
            Event = self.env["event.event"]
            # Look for a partner with that email
            email = vals.get("email").replace("%", "").replace("_", "\\_")

            # This is the change
            attendee_partner = self._find_best_matching_partner(email)

            event = Event.browse()
            if vals.get("event_id"):
                event = Event.browse(vals["event_id"])
            if attendee_partner:
                for field in {"name", "phone"}:
                    vals[field] = vals.get(field) or attendee_partner[field]
            elif event and event.create_partner:
                # Create partner
                attendee_partner = Partner.sudo().create(self._prepare_partner(vals))
            vals["attendee_partner_id"] = attendee_partner.id
        return vals
