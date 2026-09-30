import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _has_event_ticket_lines(self):
        # Check if the invoice contains any event ticket lines
        self.ensure_one()
        return any(line._is_event_ticket_line() for line in self.invoice_line_ids)

    def _post(self, soft=True):
        # Split event ticket lines and compute their discounts automatically
        # when confirming, if enabled in settings
        auto_split = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("event_ticket_individual_invoice_lines.auto_split_on_post")
        )
        if auto_split:
            invoices_to_split = self.filtered(
                lambda move: move.state == "draft"
                and move.move_type == "out_invoice"
                and move._has_event_ticket_lines()
            )
            if invoices_to_split:
                invoices_to_split.action_split_event_ticket_lines()
                invoices_to_split.action_compute_ticket_discounts()

        return super()._post(soft)

    def action_compute_ticket_discounts(self):
        # Compute qty discounts for tickets after they have been split to individual
        # lines
        for invoice in self:
            products_on_lines = {}

            ticket_lines = invoice.invoice_line_ids.filtered(
                lambda il: il._is_event_ticket_line()
            )

            # Discounts are applied per ticket, so the lines must have been
            # split first
            if ticket_lines.filtered(lambda il: not il.event_ticket_line_split):
                raise UserError(
                    _(
                        "Split the event ticket invoice lines before computing "
                        "ticket quantity discounts."
                    )
                )

            # Group the invoice lines by product
            for line in ticket_lines:
                product_template = line.product_id.product_tmpl_id
                if product_template.id not in products_on_lines:
                    products_on_lines[product_template.id] = []
                products_on_lines[product_template.id].append(line)

            for product_template_id, invoice_lines in products_on_lines.items():
                product_template = self.env["product.template"].browse(
                    product_template_id
                )

                discounts_of_product = (
                    product_template.event_ticket_qty_discount_ids.sorted(
                        "ticket_number"
                    )
                )

                # Loop through the invoice lines where this product is present,
                # and apply discounts one by one
                for idx, line in enumerate(invoice_lines):
                    if idx < len(discounts_of_product):
                        line.discount = discounts_of_product[idx].discount
                    else:
                        # TODO: if there are more tickets bought than there are
                        # discount steps on the product, should rest of rows
                        # get the highest discount?
                        line.discount = 0.0

            invoice.message_post(
                body=_("Ticket discounts have been computed and applied.")
            )

    def action_split_event_ticket_lines(self):
        # Split each invoice line that contains a ticket product
        # into lines with qty of 1

        for invoice in self:
            if invoice.state != "draft" or invoice.move_type != "out_invoice":
                raise UserError(
                    _("This action is only available for draft customer invoices.")
                )

            new_lines = []
            lines_to_remove = self.env["account.move.line"]

            for line in invoice.invoice_line_ids:
                if line._is_event_ticket_line() and not line.event_ticket_line_split:
                    # Find the related sale line which in turn is linked to the related
                    # event registrations
                    sale_lines = line.sale_line_ids
                    if len(sale_lines) != 1:
                        raise UserError(
                            _(
                                "Invoice line '%s' must be linked to exactly "
                                "one sale order line. Split the invoice lines "
                                "manually."
                            )
                            % line.name
                        )

                    sale_line = sale_lines[0]

                    # Get all the registrations of the SO line
                    registrations = self.env["event.registration"].search(
                        [("sale_order_line_id", "=", sale_line.id)]
                    )

                    # Pull some data from the event and the registration to use
                    # as the invoice line description
                    event_name = sale_line.event_id.name or ("Event")
                    event_date = sale_line.event_id.date_begin
                    formatted_date = (
                        event_date.strftime("%d.%m.%Y") if event_date else ""
                    )

                    for registration in registrations:
                        line_data = line.copy_data({"quantity": 1.0})[0]

                        # Reconnect to the original SO line
                        line_data["sale_line_ids"] = [(6, 0, [sale_line.id])]

                        # Mark the line as split, so it won't get split again
                        line_data["event_ticket_line_split"] = True

                        # Update the line description
                        line_data[
                            "name"
                        ] = f"{event_name} {formatted_date}: {registration.name}"

                        new_lines.append(line_data)

                    lines_to_remove += line

            # Remove the old line and add the individual ones
            if new_lines:
                lines_to_remove.unlink()
                for line_vals in new_lines:
                    line_vals["move_id"] = invoice.id
                    self.env["account.move.line"].create(line_vals)

            invoice.message_post(
                body=_("Event tickets have been split into individual invoice lines.")
            )
