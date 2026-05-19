from odoo import _, models


class EventEventTicket(models.Model):
    _inherit = "event.event.ticket"

    def _get_register_modal_vat_text(self):
        ticket = self
        including_vat = _("inc. VAT")
        website = self.env["website"].get_current_website(fallback=False)
        if website.show_line_subtotals_tax_selection == "tax_excluded":
            return ""

        taxes = ticket.product_id.taxes_id.filtered(
            lambda t: t.company_id == ticket.product_id.variant_company_id
        )

        # Jos veroja ei ole, palauta tyhjä kuten alkuperäinenkin teki
        if not taxes:
            return ""

        # Yhdistä mahdollisesti useiden verojen nimet pilkulla
        tax_names = ""
        for tax in taxes:
            tax_names += f"{tax.invoice_label or tax.name}, "
        tax_names = tax_names.rstrip(", ")
        res = f"{including_vat} {tax_names}"
        return res
