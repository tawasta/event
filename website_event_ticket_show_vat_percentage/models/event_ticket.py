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
        names = ", ".join(taxes.mapped("display_name"))
        return including_vat + " " + names
