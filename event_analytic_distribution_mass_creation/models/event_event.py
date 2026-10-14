from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError

SETTING_ACCOUNT_CREATION = (
    "event_analytic_distribution_mass_creation.create_event_analytic_account"
)
SETTING_ANALYTIC_PLAN = (
    "event_analytic_distribution_mass_creation.event_analytic_plan_id"
)


class Event(models.Model):
    _inherit = "event.event"

    show_analytic_accounting_tag_warning = fields.Boolean(
        compute="_compute_show_analytic_accounting_tag_warning",
    )
    analytic_distributions_outdated = fields.Boolean(
        compute="_compute_analytic_distributions_outdated",
        # Distribution models are readable only with analytic accounting rights
        groups="analytic.group_analytic_accounting",
    )

    def _get_analytic_accounting_tags(self):
        """Find the event's tags that can be used in analytic accounting rules."""
        self.ensure_one()
        analytic_accounting_tags = []
        for tag in self.tag_ids:
            if tag.category_id.use_in_analytic_accounting_rules:
                analytic_accounting_tags.append(tag)
        return analytic_accounting_tags

    @api.depends("tag_ids.category_id.use_in_analytic_accounting_rules")
    def _compute_show_analytic_accounting_tag_warning(self):
        """Let the form warn when the event does not have exactly one usable tag."""
        for event in self:
            analytic_accounting_tags = event._get_analytic_accounting_tags()
            event.show_analytic_accounting_tag_warning = (
                len(analytic_accounting_tags) != 1
            )

    @api.depends(
        "tag_ids.category_id.use_in_analytic_accounting_rules",
        "event_ticket_ids.product_id",
    )
    def _compute_analytic_distributions_outdated(self):
        """Warn that future ticket sales would use outdated analytic accounts."""
        distribution_model_obj = self.env["account.analytic.distribution.model"]
        distribution_models = distribution_model_obj.search(
            [("event_id", "in", self._origin.ids)]
        )
        distribution_models_by_event = distribution_models.grouped("event_id")
        event_plan = self._get_event_analytic_plan()
        for event in self:
            event_models = distribution_models_by_event.get(
                event._origin, distribution_model_obj
            )
            generated_models = event._get_synced_distribution_models(event_models)
            if not generated_models:
                event.analytic_distributions_outdated = False
                continue
            event.analytic_distributions_outdated = (
                event._has_outdated_distribution_models(generated_models, event_plan)
            )

    def _get_synced_distribution_models(self, distribution_models):
        """Pick the generated models of tickets that have no manual model."""
        manual_tickets = []
        for distribution_model in distribution_models:
            if not distribution_model.generated_from_event_rules:
                manual_tickets.append(distribution_model.event_ticket_id)

        synced_models = []
        for distribution_model in distribution_models:
            if distribution_model.event_ticket_id in manual_tickets:
                # The sync skips these tickets, so the banner must not flag them
                continue
            synced_models.append(distribution_model)
        return distribution_models.browse().concat(*synced_models)

    def _has_outdated_distribution_models(self, generated_models, event_plan):
        """Compare generated models with what the tags, rules and settings give now."""
        self.ensure_one()
        analytic_accounting_tags = self._get_analytic_accounting_tags()
        if len(analytic_accounting_tags) != 1:
            # Without exactly one tag, the rules no longer back the generated models
            return True

        event_analytic_account = self.env["account.analytic.account"]
        if event_plan:
            # Unsaved form changes have a NewId; the account is coded by the real id
            event_analytic_account = self._origin._find_event_analytic_account(
                event_plan
            )
            if not event_analytic_account:
                # The models were generated before event accounts were enabled
                return True

        for distribution_model in generated_models:
            analytic_account = self._get_ticket_analytic_account(
                distribution_model.event_ticket_id, analytic_accounting_tags[0]
            )
            if not analytic_account:
                return True
            expected_distribution = self._prepare_analytic_distribution(
                analytic_account, event_analytic_account
            )
            if distribution_model.analytic_distribution != expected_distribution:
                return True
        return False

    def _get_ticket_analytic_account(self, ticket, analytic_accounting_tag):
        """Find the analytic account the ticket product's rule gives for the tag."""
        for rule in ticket.product_id.product_event_analytic_accounting_rule_ids:
            if rule.event_tag_id == analytic_accounting_tag:
                return rule.analytic_account_id
        return self.env["account.analytic.account"]

    def _is_event_analytic_account_creation_enabled(self):
        """Read the setting that turns event analytic accounts on."""
        config_parameter_obj = self.env["ir.config_parameter"].sudo()
        return bool(config_parameter_obj.get_param(SETTING_ACCOUNT_CREATION))

    def _get_event_analytic_plan(self):
        """Find the plan for event analytic accounts, if creating them is enabled."""
        analytic_plan_obj = self.env["account.analytic.plan"]
        if not self._is_event_analytic_account_creation_enabled():
            return analytic_plan_obj

        config_parameter_obj = self.env["ir.config_parameter"].sudo()
        plan_id = config_parameter_obj.get_param(SETTING_ANALYTIC_PLAN)
        return analytic_plan_obj.browse(int(plan_id or 0)).exists()

    def _check_analytic_plan_overlap(self, event_plan, analytic_accounting_tag):
        """Block generation when a rule account shares the event account's plan."""
        self.ensure_one()
        overlapping_account_names = []
        for ticket in self.event_ticket_ids:
            analytic_account = self._get_ticket_analytic_account(
                ticket, analytic_accounting_tag
            )
            if analytic_account.root_plan_id != event_plan.root_id:
                continue
            account_name = analytic_account.display_name
            if account_name not in overlapping_account_names:
                overlapping_account_names.append(account_name)

        if overlapping_account_names:
            raise UserError(
                _(
                    "The analytic accounts of the ticket product rules must not "
                    "belong to the event analytic plan %(plan)s. Change the rules "
                    "or the plan in the Events settings. Overlapping analytic "
                    "accounts: %(accounts)s",
                    plan=event_plan.display_name,
                    accounts=", ".join(overlapping_account_names),
                )
            )

    def _find_event_analytic_account(self, event_plan):
        """Find the event's own analytic account by its reference."""
        self.ensure_one()
        return self.env["account.analytic.account"].search(
            [("code", "=", str(self.id)), ("plan_id", "=", event_plan.id)],
            limit=1,
        )

    def _get_or_create_event_analytic_account(self, event_plan):
        """Reuse the event's analytic account so regenerating does not duplicate it."""
        self.ensure_one()
        event_analytic_account = self._find_event_analytic_account(event_plan)
        if event_analytic_account:
            return event_analytic_account

        return self.env["account.analytic.account"].create(
            {
                "name": self.name,
                "code": str(self.id),
                "plan_id": event_plan.id,
                "company_id": self.company_id.id,
            }
        )

    def _prepare_analytic_distribution(self, analytic_account, event_analytic_account):
        """Build the distribution in one place, so generation and checks agree."""
        # Account ids joined with a comma form one distribution line over several
        # plans, so each account gets 100%. The analytic widget uses the same format.
        account_ids = [str(analytic_account.id)]
        if event_analytic_account:
            account_ids.append(str(event_analytic_account.id))
        return {",".join(account_ids): 100}

    def _prepare_ticket_analytic_distribution_model_vals(
        self, ticket, analytic_account, event_analytic_account
    ):
        """Keep the generated distribution model values in one overridable place."""
        self.ensure_one()
        company = self.company_id or analytic_account.company_id
        return {
            "event_id": self.id,
            "event_ticket_id": ticket.id,
            "company_id": company.id,
            "analytic_distribution": self._prepare_analytic_distribution(
                analytic_account, event_analytic_account
            ),
            "generated_from_event_rules": True,
        }

    def _get_distribution_account_names(self, analytic_distribution):
        """Describe a distribution by its account names for the chatter note."""
        account_ids = []
        for distribution_key in analytic_distribution or {}:
            for account_id in distribution_key.split(","):
                account_ids.append(int(account_id))
        analytic_accounts = self.env["account.analytic.account"].browse(account_ids)
        return ", ".join(analytic_accounts.exists().mapped("display_name"))

    def _prepare_event_analytic_account(self, analytic_accounting_tag):
        """Check the event account settings and get the account, if they are on."""
        self.ensure_one()
        event_plan = self._get_event_analytic_plan()
        if self._is_event_analytic_account_creation_enabled() and not event_plan:
            raise UserError(
                _(
                    "Creating event analytic accounts is enabled in the Events "
                    "settings, but the analytic plan for them is not set."
                )
            )
        if not event_plan:
            return self.env["account.analytic.account"]

        self._check_analytic_plan_overlap(event_plan, analytic_accounting_tag)
        return self._get_or_create_event_analytic_account(event_plan)

    def _sync_ticket_distribution_models(
        self, analytic_accounting_tag, event_analytic_account
    ):
        """Create missing, update outdated and remove orphaned generated models."""
        self.ensure_one()
        distribution_model_obj = self.env["account.analytic.distribution.model"]
        existing_models = distribution_model_obj.search(
            [
                ("event_id", "=", self.id),
                ("event_ticket_id", "in", self.event_ticket_ids.ids),
            ]
        )
        existing_models_by_ticket = existing_models.grouped("event_ticket_id")
        vals_list = []
        models_to_update_by_account = {}
        models_to_remove = []
        results = {
            "created_lines": [],
            "updated_lines": [],
            "removed_ticket_names": [],
            "existing_ticket_names": [],
            "ticket_names_without_rule": [],
        }

        for ticket in self.event_ticket_ids:
            ticket_models = existing_models_by_ticket.get(
                ticket, distribution_model_obj
            )
            analytic_account = self._get_ticket_analytic_account(
                ticket, analytic_accounting_tag
            )
            manual_models = ticket_models.filtered(
                lambda model: not model.generated_from_event_rules
            )
            if manual_models:
                # Models made or unmarked by a user are theirs to maintain
                results["existing_ticket_names"].append(ticket.name)
                continue

            if not analytic_account:
                if ticket_models:
                    # A stale model would keep allocating to the old account
                    models_to_remove.append(ticket_models)
                    results["removed_ticket_names"].append(ticket.name)
                else:
                    results["ticket_names_without_rule"].append(ticket.name)
                continue

            if not ticket_models:
                vals_list.append(
                    self._prepare_ticket_analytic_distribution_model_vals(
                        ticket, analytic_account, event_analytic_account
                    )
                )
                results["created_lines"].append(
                    f"{ticket.name}: {analytic_account.display_name}"
                )
                continue

            expected_distribution = self._prepare_analytic_distribution(
                analytic_account, event_analytic_account
            )
            for distribution_model in ticket_models:
                if distribution_model.analytic_distribution == expected_distribution:
                    continue
                models_to_update_by_account.setdefault(analytic_account, [])
                models_to_update_by_account[analytic_account].append(distribution_model)
                old_account_names = self._get_distribution_account_names(
                    distribution_model.analytic_distribution
                )
                new_account_names = self._get_distribution_account_names(
                    expected_distribution
                )
                results["updated_lines"].append(
                    f"{ticket.name}: {old_account_names} → {new_account_names}"
                )

        distribution_model_obj.create(vals_list)
        for analytic_account, outdated_models in models_to_update_by_account.items():
            distribution_model_obj.concat(*outdated_models).write(
                {
                    "analytic_distribution": self._prepare_analytic_distribution(
                        analytic_account, event_analytic_account
                    )
                }
            )
        distribution_model_obj.concat(*models_to_remove).unlink()
        return results

    def action_generate_analytic_distributions(self):
        """Create or update the ticket analytic distribution models in one go."""
        self.ensure_one()
        analytic_accounting_tags = self._get_analytic_accounting_tags()
        if len(analytic_accounting_tags) != 1:
            raise UserError(
                _(
                    "The event must have exactly one tag from the tag categories "
                    "used in analytic accounting rules before analytic "
                    "distributions can be generated."
                )
            )
        analytic_accounting_tag = analytic_accounting_tags[0]

        event_analytic_account = self._prepare_event_analytic_account(
            analytic_accounting_tag
        )
        results = self._sync_ticket_distribution_models(
            analytic_accounting_tag, event_analytic_account
        )
        self._post_analytic_distribution_note(event_analytic_account, results)

    def _format_note_section(self, title, items):
        """Render one titled list of the chatter note, escaping record names."""
        if not items:
            return Markup()
        list_items = []
        for item in items:
            list_items.append(Markup("<li>%s</li>") % item)
        return Markup("<p>%s</p><ul>%s</ul>") % (title, Markup().join(list_items))

    def _post_analytic_distribution_note(self, event_analytic_account, results):
        """Store the generation result in the chatter, as the button shows no popup."""
        self.ensure_one()
        body_parts = [
            Markup("<strong>%s</strong>")
            % _("Generation of analytic distribution models for the tickets")
        ]
        if event_analytic_account:
            body_parts.append(
                Markup("<p>%s <strong>%s</strong></p>")
                % (_("Event analytic account:"), event_analytic_account.display_name)
            )
        body_parts.append(
            self._format_note_section(_("Created:"), results["created_lines"])
        )
        if not results["created_lines"]:
            body_parts.append(
                Markup("<p>%s</p>")
                % _("No new analytic distribution models were created.")
            )
        sections = [
            (_("Updated:"), results["updated_lines"]),
            (
                _("Removed, the product no longer has a rule for the event's tag:"),
                results["removed_ticket_names"],
            ),
            (
                _(
                    "Skipped, the ticket has a manually maintained analytic "
                    "distribution model:"
                ),
                results["existing_ticket_names"],
            ),
            (
                _("Skipped, the product has no rule for the tags of the event:"),
                results["ticket_names_without_rule"],
            ),
        ]
        for title, items in sections:
            body_parts.append(self._format_note_section(title, items))

        self.message_post(
            body=Markup().join(body_parts),
            subtype_xmlid="mail.mt_note",
        )
