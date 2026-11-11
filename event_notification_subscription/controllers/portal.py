from odoo import Command
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalEventInterestTags(CustomerPortal):
    def _prepare_my_account_rendering_values(self, redirect="/my", **kwargs):
        values = super()._prepare_my_account_rendering_values(
            redirect=redirect, **kwargs
        )
        # The record rule of the portal user offers only the public tags
        values["event_tags"] = request.env["event.tag"].search([])
        return values

    def _create_or_update_address(self, partner_sudo, **kwargs):
        partner_sudo, feedback = super()._create_or_update_address(
            partner_sudo, **kwargs
        )
        is_saved = "redirectUrl" in feedback
        # The tags belong to the user's own contact, not to the other addresses
        is_own_contact = partner_sudo == request.env.user.partner_id
        if (
            is_saved
            and is_own_contact
            and kwargs.get("event_interest_tags_present")
        ):
            self._save_event_interest_tags(partner_sudo)
        return partner_sudo, feedback

    def _save_event_interest_tags(self, partner_sudo):
        # The same field name is posted once per checked tag, so read all values
        posted_ids = request.httprequest.form.getlist("event_interest_tag_ids")
        tag_ids = [int(value) for value in posted_ids if value.isdecimal()]
        # The ids come from the browser: keep only the tags the user may see
        tags = request.env["event.tag"].search([("id", "in", tag_ids)])
        partner_sudo.event_interest_tags = [Command.set(tags.ids)]
