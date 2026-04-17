import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    @api.model
    def _remove_private_event_leafs(self, domain):
        """Remove any existing `is_private_event` filter from a search domain.

        The website event search domain may already be altered by another custom
        module to explicitly exclude private events from the standard listing.
        When the dedicated private-event listing is used, that previous condition
        must be removed first; otherwise the final domain may contain conflicting
        clauses such as:
            ('is_private_event', '=', False)
            ('is_private_event', '=', True)

        This helper keeps the override isolated and avoids rewriting unrelated
        parts of the incoming domain.
        """
        cleaned_domain = []

        for item in domain or []:
            if (
                isinstance(item, tuple)
                and len(item) == 3
                and item[0] == "is_private_event"
            ):
                continue

            if (
                isinstance(item, list)
                and len(item) == 3
                and item[0] == "is_private_event"
            ):
                continue

            if (
                isinstance(item, list)
                and len(item) == 1
                and isinstance(item[0], list | tuple)
                and len(item[0]) == 3
                and item[0][0] == "is_private_event"
            ):
                continue

            cleaned_domain.append(item)

        return cleaned_domain

    @api.model
    def _search_get_detail(self, website, order, options):
        """Adapt the website event search detail only for the private listing context.

        The core website search engine calls this method to build search metadata,
        including the base domain applied to event records. This override preserves
        the original behavior through `super()` and only modifies the result when
        the controller explicitly sets `private_event_listing=True` in context.

        In that private context, any pre-existing `is_private_event` domain leaf
        is removed and replaced with `('is_private_event', '=', True)`, ensuring
        that the fuzzy website search, filters and counters all operate on the
        private-event subset without breaking the standard public event listing.
        """
        res = super()._search_get_detail(website, order, options)

        if self.env.context.get("private_event_listing"):
            base_domain = self._remove_private_event_leafs(res.get("base_domain", []))
            base_domain.append([("is_private_event", "=", True)])
            res["base_domain"] = base_domain

        return res
